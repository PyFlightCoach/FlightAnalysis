from json import loads
from flightanalysis.scoring.criteria import Criteria, Exponential, Continuous, Comparison, free, Single
from flightanalysis.data import get_json_resource


class F3ASingle:
    track=Single(Exponential(3.8197186342054885,0.9999999999999999, 100), 'absolute')
    roll=Single(Exponential(2.872721387028467,1.6309297535714575, 100), 'absolute')
    angle=Single(Exponential(3.8197186342054885,0.9999999999999999, 100), 'absolute')
    distance=Single(Exponential(0.002500000000000002,1.9999999999999998, 10), 'absolute')
class F3AIntra:
    track=Continuous(Exponential(3.8197186342054885,0.9999999999999999, 10), 'absolute')
    roll=Continuous(Exponential(3.3937161800825275,1.2618595071429148, 10), 'absolute')
    distance=Continuous(Exponential(0.01,2.0, 10), 'absolute')
    radius=Continuous(Exponential(0.5,1.2920296742201793, 2), 'ratio')
    speed=Continuous(Exponential(0.15,1.0, 1), 'ratio')
    roll_rate=Continuous(Exponential(0.15,1.0, 1), 'ratio')
class F3AInter:
    radius=Comparison(Exponential(1.0,0.4306765580733931, 2), 'ratio')
    speed=Comparison(Exponential(0.25,0.8613531161467862, 10), 'ratio')
    roll_rate=Comparison(Exponential(0.25,1.1132827525593783, 2), 'ratio')
    length=Comparison(Exponential(1.0,0.6826061944859854, 3), 'ratio')
    free=Comparison(Exponential(0,1, 10), 'ratio')

class F3A:
    inter = F3AInter
    intra = F3AIntra
    single = F3ASingle


if __name__=='__main__':
    print(F3A.inter.radius)
    print(F3A.intra.radius)
    print(F3A.intra.roll)