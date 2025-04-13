from flightanalysis.scoring.criteria import (
    Single,
    Limit,
    Peak, Trough,
    Exponential,
    Continuous,
    ContinuousValue,
    Bounded,
    Comparison,
    free,
)


class IntraCrit:
    pass    
    

class InterCrit:
    pass


class Crit:
    inter = InterCrit
    intra = IntraCrit



if __name__ == "__main__":
    from flightanalysis.scoring.criteria import plot_all, plot_lookup
    plot_all(InterCrit)
