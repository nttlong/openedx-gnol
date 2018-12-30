# disable missing docstring
# pylint: disable=missing-docstring

from lettuce import step, world


@step('I have created a Discussion Tag$')
def i_created_discussion_tag(step):
    step.given('I am in Studio editing a new unit')
    world.create_component_instance(
        step=step,
        category='discussion',
    )


@step('I see three settings and their expected values$')
def i_see_only_the_settings_and_values(step):
    world.verify_all_setting_entries(
        [
            ['Display Name', "Discussion", False],
            ['Category', "Week 1", False],
            ['Subcategory', "Topic-Level Student-Visible Label", False]
        ])


@step('I edit the component$')
def i_edit_and_select_settings(_step):
    world.edit_component()
