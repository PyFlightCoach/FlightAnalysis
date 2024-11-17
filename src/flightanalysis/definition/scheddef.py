from json import dump
from typing import Tuple

import geometry as g
from flightdata import Collection, State
from schemas import ManInfo, Direction, Heading, DirectionDefinition

from flightanalysis.definition.mandef import ManDef
from flightanalysis.definition.manoption import ManOption
from flightanalysis.elements import Line
from flightanalysis.schedule import Schedule


class SchedDef(Collection):
    VType = ManDef

    def __init__(self, data: dict[str, VType] | list[VType] = None):
        super().__init__(data, check_types=False)
        assert all([v.__class__.__name__ in ["ManOption", "ManDef"] for v in self])

    def wind_def_manoeuvre(self) -> DirectionDefinition:
        for i, man in enumerate(self):
            if man.info.start.direction != Direction.CROSS:
                return DirectionDefinition(
                    manid=i,
                    direction=man.info.start.direction
                )

    def add_new_manoeuvre(self, info: ManInfo, defaults=None):
        return self.add(ManDef(info, defaults))

    def create(self):
        return Schedule([md.create() for md in self])

    def create_template(
        self, depth: float = 170, wind: Heading = Heading.LTOR
    ) -> Tuple[Schedule, State]:
        templates = []
        ipos = self[0].guess_ipos(depth, wind)

        mans = []
        for md in self:
            md: ManDef = md[md.active] if isinstance(md, ManOption) else md

            itrans = g.Transformation(
                ipos if len(templates) == 0 else templates[-1][-1].pos,
                g.Euler(
                    md.info.start.orientation.value,
                    0,
                    md.info.start.direction.wind_swap_heading(wind).value,
                )
                if len(templates) == 0
                else templates[-1][-1].att,
            )
            md.fit_box(itrans)
            man = md.create()
            templates.append(man.create_template(itrans))
            mans.append(man)
        return Schedule(mans), State.stack(templates)

    def plot(self, depth=170, wind=Heading.LTOR, **kwargs):
        sched, template = self.create_template(depth, wind)
        from plotting import plot_regions

        return plot_regions(template, "manoeuvre", **kwargs)

    def label_exit_lines(self, sti: State):
        mans = list(self.data.keys()) + ["landing"]

        meids = [sti.data.columns.get_loc(l) for l in ["manoeuvre", "element"]]

        sts = [sti.get_manoeuvre(mans[0])]

        for mo, m in zip(mans[:-1], mans[1:]):
            st = sti.get_manoeuvre(m)
            # if not 'exit_line' in sts[-1].element:
            entry_len = st.get_label_len(element="entry_line")

            st.data.iloc[: int(entry_len / 2), meids] = [mo, "exit_line"]
            sts.append(st)

        sts[0].data.iloc[
            : int(sts[0].get_label_len(element="entry_line") / 2), meids
        ] = ["tkoff", "exit_line"]

        return State.stack(sts, 0)

    def create_fcj(self, sname: str, path: str, wind=Heading.LTOR, scale=1, kind="f3a"):
        sched, template = self.create_template(170, wind)
        template = State.stack(
            [
                template,
                Line("entry_line", 30, 100)
                .create_template(template[-1])
                .label(manoeuvre="landing"),
            ]
        )

        if not scale == 1:
            template = template.scale(scale)
        if wind == Heading.RTOL:
            template = template.mirror_zy()

        fcj = self.label_exit_lines(template).create_fc_json(
            [0] + [man.info.k for man in self] + [0], sname, kind.lower()
        )

        with open(path, "w") as f:
            dump(fcj, f)

    def create_fcjs(self, sname, folder, kind="F3A"):
        winds = [Heading.RTOL, Heading.RTOL, Heading.LTOR, Heading.LTOR]
        distances = [170, 150, 170, 150]

        for wind, distance in zip(winds, distances):
            w = "A" if wind == 1 else "B"
            fname = f"{folder}/{sname}_template_{distance}_{w}.json"
            print(fname)
            self.create_fcj(sname, fname, wind, distance / 170, kind)
