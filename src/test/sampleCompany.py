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

def get_sample_company(contract_number: str) -> Company:
    # 10G Federal Supply
    company_full = Company(
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
    

    company_full_2 = Company(
        large_category="Facilities",
        sub_category="Structures",
        source="MAS".strip(),
        category="238160",
        vendor="ABSOLUTE STORAGE, LLC",
        contract_number="GS-07F-9481S".strip(),
        closed_for_new_award="",
        address1="5806 E MINERAL ROAD",
        address2="",
        city="GUADALUPE",
        state="AZ",
        zip="85283-4304",
        country="",
        phone="480-768-1618",
        email="jennifer@absoluterv.com",
        url="http://www.absoluterv.com",
        current_option_period_end_date=date(2026, 5, 14),
        ultimate_contract_end_date=date(2026, 5, 14),
        sam_uei="T2M6KVD8VXE5",
        small_business="s",
        other_than_small_business="",
        woman_owned="",
        women_owned_wosb="",
        women_owned_edwosb="",
        veteran_owned="",
        service_disabled_veteran_owned="",
        small_disadvantaged="",
        a8a="",
        a8a_sole_source_pool="",
        a8a_sole_source_exit_date=None,
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
        price_list="https://www.gsaadvantage.gov/ref_text/GS07F9481S/GS07F9481S_online.htm",
        view_catalog="https://www.gsaelibrary.gsa.gov/ElibMain/advRedirect.do?contract=GS-07F-9481S&sin=238160&app=cat"
    )
    
    # company_under_100
    company_under_100 = Company(
        large_category="Facilities",
        sub_category="Structures",
        source="MAS".strip(),
        category="238160",
        vendor="ACE ROOF COATINGS, INC",
        contract_number="GS-07F-177AA".strip(),
        closed_for_new_award="",
        address1="4821 GRISHAM DR",
        address2="",
        city="ROWLETT",
        state="TX",
        zip="75088-3950",
        country="",
        phone="972-864-0240",
        email="emendel@arccoat.com",
        url="http://WWW.ARCHITECTURALROOFCOAT.COM",
        current_option_period_end_date=date(2028, 3, 14),
        ultimate_contract_end_date=date(2033, 3, 14),
        sam_uei="HC97VH2FHKB8",
        small_business="s",
        other_than_small_business="",
        woman_owned="",
        women_owned_wosb="",
        women_owned_edwosb="",
        veteran_owned="",
        service_disabled_veteran_owned="",
        small_disadvantaged="",
        a8a="",
        a8a_sole_source_pool="",
        a8a_sole_source_exit_date=None,
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
        price_list="",
        view_catalog="https://www.gsaelibrary.gsa.gov/ElibMain/advRedirect.do?contract=GS-07F-177AA&sin=238160&app=cat"
    )

    company_labor = Company(
        large_category="Facilities",
        sub_category="Services",
        source="MAS".strip(),
        category="238160",
        vendor="CORPORATE EVENTS AND OCCASIONS, LLC",
        contract_number="47QRAA22D000T".strip(),
        closed_for_new_award="",
        address1="4821 GRISHAM DR",
        address2="",
        city="ROWLETT",
        state="TX",
        zip="75088-3950",
        country="",
        phone="972-864-0240",
        email="emendel@arccoat.com",
        url="http://WWW.ARCHITECTURALROOFCOAT.COM",
        current_option_period_end_date=date(2028, 3, 14),
        ultimate_contract_end_date=date(2033, 3, 14),
        sam_uei="HC97VH2FHKB8",
        small_business="s",
        other_than_small_business="",
        woman_owned="",
        women_owned_wosb="",
        women_owned_edwosb="",
        veteran_owned="",
        service_disabled_veteran_owned="",
        small_disadvantaged="",
        a8a="",
        a8a_sole_source_pool="",
        a8a_sole_source_exit_date=None,
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
        price_list="",
        view_catalog="https://www.gsaelibrary.gsa.gov/ElibMain/advRedirect.do?contract=GS-07F-177AA&sin=238160&app=cat"
    )
    
    company_list = [company_full, company_full_2, company_under_100, company_labor]

    for company in company_list:
        if company.contract_number != contract_number:
            continue
        else:
            print(f"Company Found: {company.vendor}")
            return company




