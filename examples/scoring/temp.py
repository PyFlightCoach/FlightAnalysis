class F3ASingle:
    track=Single(Exponential(3.393716180082528,1.2618595071429148), 'absolute')
    roll=Single(Exponential(3.1486776615143057,1.4278157399964433), 'absolute')
    angle=Single(Exponential(3.8197186342054863,1.000000000000001), 'absolute')
    distance=Single(Exponential(0.0012499999999988631,2.0000000000002465), 'absolute')
class F3AIntra:
    track=Continuous(Exponential(3.393716180082528,1.2618595071429148), 'absolute')
    roll=Continuous(Exponential(3.1486776615143057,1.4278157399964433), 'absolute')
    radius=Continuous(Exponential(1.0,1.2618595071429148), 'ratio')
    speed=Continuous(Exponential(0.14999999999999858,1.0000000000000058), 'ratio')
    roll_rate=Continuous(Exponential(0.14999999999999858,1.0000000000000058), 'ratio')
class F3AInter:
    radius=Comparison(Exponential(0.5,0.861353116146786), 'ratio')
    speed=Comparison(Exponential(0.5,0.2519296364125925), 'ratio')
    roll_rate=Comparison(Exponential(0.14999999999999858,1.0000000000000058), 'ratio')
    length=Comparison(Exponential(0.5,1.1132827525593783), 'ratio')
    free=Comparison(Exponential(0,1), 'ratio')