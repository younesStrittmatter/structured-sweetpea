from mate_strategy.schema.wrapper import GenericWrapper
from mate_structure.sweetpea.schema import LevelSchema

from sweetpea import Level


class LevelWrapper(GenericWrapper[Level]):
    Schema = LevelSchema

    @staticmethod
    def _to_domain_impl(d):
        return Level(name=d["weight"], weight=d["weight"] or 1)
