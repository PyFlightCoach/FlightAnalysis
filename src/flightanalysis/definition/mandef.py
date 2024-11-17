"""This module contains the structures used to describe the elements within a manoeuvre and
their relationship to each other.

A Manoeuvre contains a dict of elements which are constructed in order. The geometry of these
elements is described by a set of high level parameters, such as loop radius, combined line
length of lines, roll direction.

A complete manoeuvre description includes a set of functions to create the elements based on
the higher level parameters and another set of functions to collect the parameters from the
elements collection.

"""

from __future__ import annotations

from dataclasses import dataclass

import geometry as g
from flightdata import State
from loguru import logger
from schemas.maninfo import ManInfo, Position
from schemas.positioning import Heading

from flightanalysis.elements import Elements
from flightanalysis.manoeuvre import Manoeuvre
from flightanalysis.scoring.box import Box

from . import ElDef, ElDefs, ManParms


@dataclass
class ManDef:
    """This is a class to define a manoeuvre for template generation and judging.
    It contains information on the location of the manoeuvre (ManInfo), a set
    of parameters that are used to define the scale of the manoevre (ManParms)
    and a list of element definitions that are used to create the elements that
    form the manoeuvre (ElDefs).
    """

    info: ManInfo
    mps: ManParms
    eds: ElDefs
    box: Box

    def __repr__(self):
        return f"ManDef({self.info.name})"

    @property
    def uid(self):
        return self.info.short_name
    
    def to_dict(self, dgs=True) -> dict:
        return dict(
            info=self.info.to_dict(),
            mps=self.mps.to_dict(),
            eds=self.eds.to_dict(dgs),
            box=self.box.to_dict(),
        )

    @staticmethod
    def from_dict(data: dict | list) -> ManDef | ManOption:
        if isinstance(data, list):
            return ManOption.from_dict(data)
        elif (
            "options" in data
            and data["options"] is not None
            and len(data["options"]) > 0
        ):
            opts = data.pop("options")
            return ManOption.from_dict([data] + opts)
        else:
            info = ManInfo.from_dict(data["info"])
            mps = ManParms.from_dict(data["mps"])
            eds = ElDefs.from_dict(data["eds"], mps)
            box = Box.from_dict(data["box"])
            return ManDef(info, mps, eds, box)

    def guess_ipos(self, target_depth: float, heading: Heading) -> g.Transformation:
        gpy = g.PY(target_depth)
        return g.Point(
            x={
                Position.CENTRE: {
                    Heading.OUTTOIN: 0.0,
                    Heading.INTOOUT: 0.0,
                    Heading.RTOL: self.box.right_pos(gpy).x[0],
                    Heading.LTOR: self.box.left_pos(gpy).x[0],
                }[heading],
                Position.END: 0.0,
            }[self.info.position],
            y={
                Heading.OUTTOIN: 2 * target_depth,
                Heading.INTOOUT: 0,
                Heading.RTOL: target_depth,
                Heading.LTOR: target_depth,
            }[heading],
            z=self.box.bottom(gpy)[1][0] * (self.info.start.height.value - 1)
            + self.info.start.height.value * self.box.top(gpy)[1][0],
        )

    def initial_rotation(self, heading: Heading) -> g.Quaternion:
        return g.Euler(self.info.start.orientation.value, 0, heading.value)

    def guess_itrans(self, target_depth: float, heading: Heading) -> g.Transformation:
        return g.Transformation(
            self.guess_ipos(target_depth, heading), self.initial_rotation(heading)
        )

    def entry_line_length(self, itrans: g.Transformation, target_depth=None) -> float:
        """Calculate the length of the entry line so that the manoeuvre is centred
        or extended to box edge as required.

        Args:
            itrans (Transformation): The location to draw the line from, usually the
                                        end of the last manoeuvre.

        Returns:
            float: the line length
        """
        target_depth = target_depth or self.box.middle().y[0]
        heading = Heading.infer(itrans.rotation.bearing())

        logger.debug(
            f"Calculating entry line length for {self.info.position.name} manoeuvre {self.info.name}"
        )
        logger.debug(f"Target depth: {target_depth:.0f}, heading: {heading.name}")

        # Create a template at zero to work out how much space the manoueuvre needs
        man = Manoeuvre(
            Elements([ed(self.mps) for ed in self.eds[1:]]),
            None,
            uid=self.info.name,
        )

        template = man.create_template(State.from_transform(itrans))

        if self.info.position == Position.CENTRE and (
            heading == Heading.LTOR or heading == Heading.RTOL
        ):
            if len(self.info.centre_points) > 0:
                xoffset = (
                    man.elements[self.info.centre_points[0] - 1]
                    .get_data(template)
                    .pos.x[0]
                )
            elif len(self.info.centred_els) > 0:
                ce, fac = self.info.centred_els[0]
                _x = man.elements[ce - 1].get_data(template).pos.x
                xoffset = _x[int(len(_x) * fac)]
            else:
                xoffset = (max(template.pos.x) + min(template.pos.x)) / 2
            return -itrans.att.transform_point(g.PX(xoffset)).x[0]

        else:
            bound = {
                Heading.LTOR: "right",
                Heading.RTOL: "left",
                Heading.INTOOUT: "back",
                Heading.OUTTOIN: "front",
            }[heading]
            logger.debug(f"Bound: {bound}")

            return min(getattr(self.box, bound)(template.pos)[1])

    def fit_box(self, itrans: g.Transformation, target_depth=None):
        self.eds.entry_line.props["length"] = self.entry_line_length(
            itrans, target_depth
        )
        return self

    def create(self) -> Manoeuvre:
        """Create the manoeuvre based on the default values in self.mps."""
        return Manoeuvre(
            Elements([ed(self.mps) for ed in self.eds]),
            None,
            uid=self.info.short_name,
        )

    def plot(self, depth=170, heading=Heading.LTOR):
        itrans = self.guess_itrans(depth, heading)
        man = self.create()
        template = man.create_template(itrans)
        from plotting import plotdtw, plotsec

        fig = plotdtw(template, template.data.element.unique())
        fig = plotsec(template, fig=fig, nmodels=20, scale=3)
        return fig

    def update_dgs(self, applicator: callable):
        new_eds = []

        man = self.create()
        tp = man.create_template(self.guess_itrans(170, Heading.LTOR))

        for i, ed in enumerate(self.eds):
            new_eds.append(
                ElDef(
                    ed.name,
                    ed.Kind,
                    ed.props,
                    applicator(
                        man.elements[i],
                        tp.get_element(ed.name),
                        self.eds[i - 1].Kind if i > 0 else "",
                        self.eds[i + 1].Kind if i < len(self.eds) - 1 else "",
                    ),
                )
            )
        return ManDef(self.info, self.mps, ElDefs(new_eds), self.box)


from .manoption import ManOption  # noqa: E402
