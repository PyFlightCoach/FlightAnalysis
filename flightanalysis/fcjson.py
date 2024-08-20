from pydantic import BaseModel
import pandas as pd
import datetime
from json import load
import re


class FCJData(BaseModel):
    VN: float = None
    VE: float = None
    VD: float = None
    dPD: float = None  #
    r: float
    p: float
    yw: float
    N: float
    E: float
    D: float
    time: int
    roll: float
    pitch: float
    yaw: float


class FCJParameters(BaseModel):
    rotation: float
    start: int
    stop: int
    moveEast: float
    moveNorth: float
    wingspan: float
    modelwingspan: float
    elevate: float
    originLat: float
    originLng: float
    originAlt: float
    pilotLat: str
    pilotLng: str
    pilotAlt: str
    centerLat: str
    centerLng: str
    centerAlt: str
    schedule: list[str]


class FCJView(BaseModel):
    position: dict
    target: dict


class FCJMan(BaseModel):
    name: str
    k: float
    id: str
    sp: int
    wd: float
    start: int
    stop: int
    sel: bool
    background: str


class FCJHumanResult(BaseModel):
    name: str
    date: datetime.date
    scores: list[float]


class El(BaseModel):
    name: str
    start: int
    stop: int


class ScoreProps(BaseModel):
    difficulty: int
    truncate: bool


class Score(BaseModel):
    intra: float
    inter: float
    positioning: float
    total: float


class Result(BaseModel):
    score: Score
    properties: ScoreProps


class FCJManResult(BaseModel):
    els: list[El]
    results: list[Result]

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            data=[res.score.__dict__ for res in self.results],
            index=pd.MultiIndex.from_frame(
                pd.DataFrame([res.properties.__dict__ for res in self.results])
            ),
        )


class FCJResult(BaseModel):
    fa_version: str
    manresults: list[FCJManResult | None]

    def to_df(self) -> pd.DataFrame:
        return pd.concat(
            {i: fcjmr.to_df() for i, fcjmr in enumerate(self.manresults[1:]) if fcjmr},
            axis=0,
            names=["manoeuvre", "difficulty", "truncate"],
        )


class FCJ(BaseModel):
    version: str
    comments: str
    name: str
    view: FCJView
    parameters: FCJParameters
    scored: bool
    scores: list[float]
    human_scores: list[FCJHumanResult] = []
    fcs_scores: list[FCJResult] = []
    mans: list[FCJMan]
    data: list[FCJData]
    jhash: int | None = None

    def score_df(self):
        return pd.concat(
            {fcjr.fa_version: fcjr.to_df() for fcjr in self.fcs_scores},
            axis=0,
            names=["version", "manoeuvre", "difficulty", "truncate"],
        )

    def man_df(self):
        return pd.DataFrame(
            [man.__dict__ for man in self.mans[1:-1]],
            index=pd.Index(range(len(self.mans[1:-1])), name="manoeuvre"),
        )

    def pfc_version_df(self):
        sdf = self.score_df().loc[pd.IndexSlice[:, :, 3, False]]
        return pd.concat(
            [sdf, sdf.mul(self.man_df().k, axis=0)], axis=1, keys=["raw", "kfac"]
        )

    def version_summary_df(self):
        return self.pfc_version_df().groupby("version").kfac.sum()

    def latest_version(self):
        return max([fcjr.fa_version for fcjr in self.fcs_scores])

    @property
    def id(self):
        return re.search(r"\d{8}", self.name)[0]

    @property
    def created(self):
        return datetime.datetime.strptime(
            re.search(r"_\d{2}_\d{2}_\d{2}_", self.name)[0], "_%y_%m_%d_"
        )


def get_scores(file: str) -> pd.DataFrame:
    fcj = FCJ.model_validate_json(open(file, "r").read())
    return fcj.pfc_version_df()
