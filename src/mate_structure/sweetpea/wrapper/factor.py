# structured_sweetpea/wrappers/factor.py
from sweetpea import Factor
from mate_strategy.schema.wrapper import GenericWrapper
from mate_structure.sweetpea.schema.factor import FactorSchema
from mate_structure.sweetpea.schema.level import Level, DerivedLevel

class FactorWrapper(GenericWrapper[Factor]):
    Schema = FactorSchema

    @staticmethod
    def _to_domain_impl(d):

        levels = [l if isinstance(l, str)
                  else DerivedLevelWrapper.from_dict(l).to_sweetpea()
                  for l in d["levels"]]
        return Factor(d["name"], levels)

    @staticmethod
    def _to_dict_impl(f):
        from .derived_level import DerivedLevelWrapper
        out = []
        for lvl in f.levels:
            out.append(lvl.name if isinstance(lvl, str)
                        else DerivedLevelWrapper.from_sweetpea(lvl).json())
        return {"name": f.name, "levels": out}
