from django import template
from tools import odm_handling

register = template.Library()


@register.filter(name="odm_para")
def odm_para(arg1: str):
    return dict(odm_handling.get_def_value_dict(odm_handling.match_odm_by_name(arg1))).keys(),


