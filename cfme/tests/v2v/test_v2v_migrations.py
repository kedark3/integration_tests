"""Test to validate basic navigations.Later to be replaced with End-to-End functional testing."""
import fauxfactory
import pytest

from widgetastic.exceptions import NoSuchElementException

from cfme.fixtures.provider import rhel74_template
from cfme.infrastructure.provider.rhevm import RHEVMProvider
from cfme.infrastructure.provider.virtualcenter import VMwareProvider
from cfme.markers.env_markers.provider import ONE_PER_VERSION
from cfme.utils.appliance.implementations.ui import navigate_to, navigator

from cfme.utils.wait import wait_for

pytestmark = [
    pytest.mark.ignore_stream('5.8'),
    pytest.mark.provider(
        classes=[RHEVMProvider],
        selector=ONE_PER_VERSION
    ),
    pytest.mark.provider(
        classes=[VMwareProvider],
        selector=ONE_PER_VERSION,
        fixture_name='second_provider'
    )
]


@pytest.mark.parametrize('form_data_vm_obj_single_datastore', [['nfs', 'nfs', rhel74_template],
                            ['nfs', 'iscsi', rhel74_template], ['iscsi', 'iscsi', rhel74_template]],
                        indirect=True)
def test_single_datastore_single_vm_migration(request, appliance, providers, conversion_host_setup,
                                            form_data_vm_obj_single_datastore,
                                            enable_disable_migration_ui,
                                            soft_assert):
    # TODO: This test case does not support update
    # as update is not a supported feature for mapping.
    infrastructure_mapping_collection = appliance.collections.v2v_mappings
    mapping = infrastructure_mapping_collection.create(form_data_vm_obj_single_datastore[0])
    migration_plan_collection = appliance.collections.v2v_plans
    migration_plan_collection.create(name="plan_{}".format(fauxfactory.gen_alphanumeric()),
                description="desc_{}".format(fauxfactory.gen_alphanumeric()),
                infra_map=mapping.name,
                vm_list=form_data_vm_obj_single_datastore[1], start_migration=True)

    view = appliance.browser.create_view(navigator.get_class(migration_plan_collection, 'All').VIEW)
    # explicit wait for spinner of in-progress status card
    wait_for(lambda: bool(view.progress_bar.is_plan_started(migration_plan_collection.name)),
             message="migration plan is starting, be patient please", delay=5, num_sec=3600)
    assert view._get_status(migration_plan_collection.name) == "Completed Plans"

    view = navigate_to(infrastructure_mapping_collection, 'All', wait_for_view=True)
    mapping_list = view.infra_mapping_list
    mapping_list.delete_mapping(mapping.name)


@pytest.mark.parametrize('form_data_single_network', [['VM Network', 'ovirtmgmt'],
                            ['DPortGroup', 'ovirtmgmt']], indirect=True)
def test_single_network_single_vm_mapping_crud(appliance, conversion_tags, providers,
                                               form_data_single_network):
    # TODO: This test case does not support update
    # as update is not a supported feature for mapping.
    infrastructure_mapping_collection = appliance.collections.v2v_mappings
    mapping = infrastructure_mapping_collection.create(form_data_single_network)
    view = navigate_to(infrastructure_mapping_collection, 'All', wait_for_view=True)
    assert mapping.name in view.infra_mapping_list.read()
    mapping_list = view.infra_mapping_list
    mapping_list.delete_mapping(mapping.name)
    view.browser.refresh()
    view.wait_displayed()
    try:
        assert mapping.name not in view.infra_mapping_list.read()
    except NoSuchElementException:
        # meaning there was only one mapping that is deleted, list is empty
        pass


@pytest.mark.parametrize('form_data_dual_datastore', [[['nfs', 'nfs'], ['iscsi', 'iscsi']],
                            [['nfs', 'local'], ['iscsi', 'iscsi']]], indirect=True)
def test_dual_datastore_dual_vm_mapping_crud(appliance, form_data_dual_datastore, migration_ui,
                                             providers):
    # TODO: Add "Delete" method call.This test case does not support update/delete
    # as update is not a supported feature for mapping,
    # and delete is not supported in our automation framework.
    infrastructure_mapping_collection = appliance.collections.v2v_mappings
    mapping = infrastructure_mapping_collection.create(form_data_dual_datastore)
    view = navigate_to(infrastructure_mapping_collection, 'All', wait_for_view=True)
    assert mapping.name in view.infra_mapping_list.read()
    mapping_list = view.infra_mapping_list
    mapping_list.delete_mapping(mapping.name)
    view.browser.refresh()
    view.wait_displayed()
    try:
        assert mapping.name not in view.infra_mapping_list.read()
    except NoSuchElementException:
        # meaning there was only one mapping that is deleted, list is empty
        pass


@pytest.mark.parametrize('vm_list', ['NFS_Datastore_1', 'iSCSI_Datastore_1'], ids=['NFS', 'ISCSI'],
                         indirect=True)
@pytest.mark.parametrize('form_data_single_datastore', [['nfs', 'nfs']], indirect=True)
def test_end_to_end_migration(appliance, migration_ui, providers, form_data_single_datastore,
                              vm_list):
    infrastructure_mapping_collection = appliance.collections.v2v_mappings
    mapping = infrastructure_mapping_collection.create(form_data_single_datastore)
    coll = appliance.collections.v2v_plans
    coll.create(name="plan_{}".format(fauxfactory.gen_alphanumeric()),
                description="desc_{}".format(fauxfactory.gen_alphanumeric()),
                infra_map=mapping.name,
                vm_list=vm_list,
                start_migration=True)
    view = appliance.browser.create_view(navigator.get_class(coll, 'All').VIEW)
    # explicit wait for spinner of in-progress status card
    wait_for(lambda: bool(view.progress_bar.is_plan_started(coll.name)),
             message="migration plan is starting, be patient please", delay=5, num_sec=120)
    assert view._get_status(coll.name) == "Completed Plans"


def test_conversion_host_tags(appliance, providers):
    """Tests following cases:

    1)Test Attribute in UI indicating host has/has not been configured as conversion host like Tags
    2)Test converstion host tags
    """
    tag1 = (appliance.collections.categories.instantiate(
            display_name='V2V - Transformation Host *')
            .collections.tags.instantiate(display_name='t'))

    tag2 = (appliance.collections.categories.instantiate(
            display_name='V2V - Transformation Method')
            .collections.tags.instantiate(display_name='VDDK'))

    host = providers[1].hosts[0]
    # Remove any prior tags
    host.remove_tags(host.get_tags())

    host.add_tag(tag1)
    assert host.get_tags()[0].category.display_name in tag1.category.display_name
    host.remove_tag(tag1)

    host.add_tag(tag2)
    assert host.get_tags()[0].category.display_name in tag2.category.display_name
    host.remove_tag(tag2)

    host.remove_tags(host.get_tags())
