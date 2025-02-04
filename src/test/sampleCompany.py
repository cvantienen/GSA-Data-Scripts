from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Company:
    large_category: Optional[str] = None
    sub_category: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    vendor: Optional[str] = None
    contract_number: Optional[str] = None
    closed_for_new_award: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    url: Optional[str] = None
    current_option_period_end_date: Optional[date] = None
    ultimate_contract_end_date: Optional[date] = None
    sam_uei: Optional[str] = None
    small_business: Optional[str] = None
    other_than_small_business: Optional[str] = None
    woman_owned: Optional[str] = None
    women_owned_wosb: Optional[str] = None
    women_owned_edwosb: Optional[str] = None
    veteran_owned: Optional[str] = None
    service_disabled_veteran_owned: Optional[str] = None
    small_disadvantaged: Optional[str] = None
    a8a: Optional[str] = None
    a8a_sole_source_pool: Optional[str] = None
    a8a_sole_source_exit_date: Optional[date] = None
    hub_zone: Optional[str] = None
    tribally_owned_firm: Optional[str] = None
    american_indian_owned: Optional[str] = None
    alaskan_native_corporation_owned_firm: Optional[str] = None
    native_hawaiian_organization_owned_firm: Optional[str] = None
    a8a_joint_venture_eligible: Optional[str] = None
    women_owned_joint_venture_eligible: Optional[str] = None
    service_disabled_veteran_owned_joint_venture_eligible: Optional[str] = None
    hubzone_joint_venture_eligible: Optional[str] = None
    state_local: Optional[str] = None
    t_and_cs: Optional[str] = None
    price_list: Optional[str] = None
    view_catalog: Optional[str] = None

    def __str__(self):
        return self.vendor or "Unknown Vendor"

def get_sample_company(contract_number):
    print(contract_number)
    # Now you can create a test object without having to import the real Django model.
    sample_company = Company(
        large_category="Facilities",
        sub_category="Structures",
        source="MAS".strip(),
        category="238160",
        vendor="10G Federal Supply",
        contract_number="47QSEA20D003B".strip(),
        closed_for_new_award="",
        address1="91-567 NUKUAWA ST",
        address2="",
        city="KAPOLEI",
        state="HI",
        zip="96707-1801",
        country="",  # Optionally, you might set this to "USA"
        phone="808-682-8096",
        email="jclark@usacom.org",
        url="http://ateampacificroofing.com",
        current_option_period_end_date=date(2029, 7, 31),
        ultimate_contract_end_date=date(2044, 7, 31),
        sam_uei="H9HTJ3JKMZ74",
        small_business="s",
        other_than_small_business="",
        woman_owned="",
        women_owned_wosb="",
        women_owned_edwosb="",
        veteran_owned="",
        service_disabled_veteran_owned="",
        small_disadvantaged="d",
        a8a="",
        a8a_sole_source_pool="",
        a8a_sole_source_exit_date=None,  # No date provided in sample
        hub_zone="",
        tribally_owned_firm="",
        american_indian_owned="",
        alaskan_native_corporation_owned_firm="",
        native_hawaiian_organization_owned_firm="",
        a8a_joint_venture_eligible="",
        women_owned_joint_venture_eligible="",
        service_disabled_veteran_owned_joint_venture_eligible="",
        hubzone_joint_venture_eligible="",
        state_local="",
        t_and_cs="",
        price_list="https://www.gsaelibrary.gsa.gov/ElibMain/advRedirect.do?contract=47QSMS24D00AP&sin=238160&app=cat",
        view_catalog="https://www.gsaadvantage.gov/ref_text/47QSMS24D00AP/47QSMS24D00AP_online.htm"
    )

    return sample_company
