from flightanalysis.scoring.criteria import Single, Exponential, ContAbs, ContRat, InsideBound, MaxBound, Comparison

class F3ASingle:
    track=Single(Exponential(3.8197186342054885,0.9999999999999999, 100 ))
    roll=Single(Exponential(2.872721387028467,1.6309297535714575, 100 ))
    angle=Single(Exponential(3.8197186342054885,0.9999999999999999, 100 ))
    distance=Single(Exponential(0.02500000000000001,0.9999999999999999, None ))
class F3AIntra:
    track=ContAbs(Exponential(3.8197186342054885,0.9999999999999999, None ))
    roll=ContAbs(Exponential(3.3937161800825275,1.2618595071429148, None ))
    radius=ContRat(Exponential(0.5,1.2920296742201793, 2 ))
    speed=ContRat(Exponential(0.15,1.0, 1 ))
    roll_rate=ContRat(Exponential(0.15,1.0, 1 ))
    stallturn_speed=InsideBound(Exponential(0.08879139070041006,1.75647079736603, None ), [-2, 2])
    stallturn_width=InsideBound(Exponential(0.14798565116735013,1.75647079736603, None ), [-2, 2])
    spin_entry_length=InsideBound(Exponential(0.08879139070041006,1.75647079736603, None ), [-5, 5])
    pitch_break_length=InsideBound(Exponential(0.7,2.321928094887362, None ), [-2, 2])
    recovery_length=MaxBound(Exponential(0.7,2.321928094887362, None ), 2)
class F3AInter:
    radius=Comparison(Exponential(1.0,0.4306765580733931, 2 ))
    speed=Comparison(Exponential(0.25,0.8613531161467862, None ))
    roll_rate=Comparison(Exponential(0.25,1.1132827525593783, 2 ))
    length=Comparison(Exponential(1.0,0.6826061944859854, 3 ))
    free=Comparison(Exponential(0,1, None ))



class F3A:
    inter = F3AInter
    intra = F3AIntra
    single = F3ASingle


if __name__=='__main__':
    print(F3A.inter.radius)
    print(F3A.intra.radius)
    print(F3A.intra.roll)