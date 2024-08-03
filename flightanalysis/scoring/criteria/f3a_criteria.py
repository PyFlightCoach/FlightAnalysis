from flightanalysis.scoring.criteria import Single, Exponential, ContAbs, ContRat, InsideBound, MaxBound, Comparison, OutsideBound

### Generated code ###
class F3ASingle:
    track=Single(Exponential(3.8197186342054885,0.9999999999999999, 6 ))
    roll=Single(Exponential(2.872721387028467,1.6309297535714575, 6 ))
    angle=Single(Exponential(3.8197186342054885,0.9999999999999999, 6 ))
class F3AIntra:
    track=ContAbs(Exponential(3.6157124327118417,1.12154551155295, 6 ), 4)
    roll=ContAbs(Exponential(3.148677661514303,1.427815739996445, 6 ), 1)
    radius=ContRat(Exponential(0.3333333333333333,1.0, 1 ), 0.5)
    speed=ContRat(Exponential(0.15,1.0, 1 ), 4)
    roll_rate=ContRat(Exponential(0.3,1.0, 0.5 ), 1)
    autorotation_rate=ContRat(Exponential(0.3,1.0, 0.5 ), 2)
    stallturn_speed=InsideBound(Exponential(0.08879139070041006,1.75647079736603, None ), [-2, 2])
    stallturn_width=InsideBound(Exponential(0.14798565116735013,1.75647079736603, None ), [-2, 2])
    break_angle=OutsideBound(Exponential(45.83662361046588,1.0000000000000002, None ), [-0.1308996938995747, 0.1308996938995747])
    nose_drop_amount=OutsideBound(Exponential(20,1, None ), [-0.2617993877991494, 0.2617993877991494])
    recovery_length=MaxBound(Exponential(0.7,2.321928094887362, None ), 2)
    box=InsideBound(Exponential(76.39437268410977,1, None ), [-1.0471975511965976, 1.0471975511965976])
    depth=MaxBound(Exponential(0.02500000000000001,0.9999999999999999, None ), 170)
class F3AInter:
    radius=Comparison(Exponential(1.0,1.0, 2 ))
    speed=Comparison(Exponential(0,1, None ))
    roll_rate=Comparison(Exponential(0.25,1.0000000000000002, 1 ))
    length=Comparison(Exponential(1.0,1.0, 2 ))
    free=Comparison(Exponential(0,1, None ))
### End Generated code ###

class F3A:
    inter = F3AInter
    intra = F3AIntra
    single = F3ASingle

