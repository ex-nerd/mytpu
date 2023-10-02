"""
Classes built based on the data that I've scraped.
Untyped values mean I haven't yet seen them contain data other than null or []
"""
from tkinter import N
from typing import Any, ForwardRef, Generator, List, Optional, Set, Type, TypeVar, Dict, Union
import json
from attr import define, field
# from cattr import GenConverter
import cattr

CustomerID = str  # string value of the numeric(?) customer id
AccountNumber = str  # string value of the numeric(?) account number
PersonID = str  # string value of the numeric(?) person id
UserID = str  # username in all caps (I guess their user names are not case sensitive)

# Not in love with this name (maybe ModelClass instead?) but it works for now.
ModelType = TypeVar("ModelType", bound="Model")


# @define(auto_attribs=True, slots=True, kw_only=True)
class Model:
    @classmethod
    def from_dict(cls: Type[ModelType], data: Dict[str, Any]) -> ModelType:
        """
        Instantiates a model of the appropriate type, populated from the data in the
        provided dict.

        Properties will be recursively processed based on type hints.

        Args:
            data (Dict): dict to convert

        Returns:
            T: Instance of the model (sub)class
        """
        return cattr.structure(data, cls)

    def as_json(self) -> str:
        return json.dumps(self.unstructure)

    def unstructure(self) -> Any:
        return cattr.unstructure(self)


@define(auto_attribs=True, slots=True, kw_only=True)
class Response(Model):
    """
    This is intended as an abstract class to track standard
    response properties.
    """
    status: str = field(default=None)  # "Ok"
    statusCode: str = field(default=None)  # "200"
    validations: Union[List, None] = field(default=None)
    requestTransactionId: str = field(default=None)  # string formatted uuid

@define(auto_attribs=True, slots=True, kw_only=True)
class Account(Model):
    """
    This is called "Account" but the quantity of data suggests it's more like a summary.
    The "AccountSummary" type has much more info.
    """

    access: str = field(default=None)  # "P"
    accountAlreadyRegistrd: Any = field(default=None)
    accountBalance: Any = field(default=None)
    accountNickName: str = field(default=None)  # ""
    accountNumber: AccountNumber = field(
        default=None
    )  # string containing numeric account number
    accountStatus: Any = field(default=None)
    addressDetails: Any = field(default=None)
    customerId: CustomerID = field(default=None)
    defaultAccountInd: str = field(default=None)  # "Y",
    firstName: str = field(default=None)
    highbillThreshold: Any = field(default=None)
    isHidden: Any = field(default=None)
    lastName: str = field(default=None)
    linkedAccounts: Any = field(default=None)
    maskedAccountNumber: Any = field(default=None)
    personId: PersonID = field(default=None)
    premiseInfo: Any = field(default=None)
    registerNumber: Any = field(default=None)
    serviceAddress: str = field(default=None)  # full address: `street,city state zip`
    serviceAddressLine1: str = field(
        default=None
    )  # first line of street address but often has house number redacted to XXXXX
    sharedAccessType: Any = field(default=None)
    validated: Any = field(default=None)


@define(auto_attribs=True, slots=True, kw_only=True)
class User(Model):
    accounts: Union[List, None] = field(default=None)  # seems to always be empty
    convertedEbill: str = field(default=None)  # "N"
    convertedUser: str = field(default=None)  # "Y"
    convertedUserPassword: str = field(default=None)  # "false"
    customerId: CustomerID = field(default=None)
    customerType: str = field(default=None)  # "RES"
    defaultAccount: Account = field(default=None)
    emailAddress: str = field(default=None)  # often allcaps
    firstName: str = field(default=None)
    firstTimeLogin: str = field(default=None)  # "N"
    invalidLoginCount: int = field(
        default=None
    )  # number of failed login attempts? Should be a zero
    lastfailedLoginDate: str = field(default=None)  # "YYYY-MM-DD HH:MM:SS",
    lastName: str = field(default=None)  # "PETERSEN",
    socialInd: bool = field(default=None)  # false
    userName: UserID = field(default=None)


@define(auto_attribs=True, slots=True, kw_only=True)
class UserDetailsResponse(Response):
    """
    why two separate user formats?!?
    This is the raw format returned from /rest/user and
    definitely needs to be cleaned up.
    """
    user: User = field(default=None)
    emails: Union[List, None] = field(default=None)
    phones: Union[List, None] = field(default=None)
    notifications: Union[List, None] = field(default=None)
    banks: Union[List, None] = field(default=None)
    ebillPhoneAlert: bool = field(default=None)  # false


@define(auto_attribs=True, slots=True, kw_only=True)
class Address(Model):
    AddressLine1: str = field(default=None)
    AddressLine2: str = field(default=None)
    AddressLine3: str = field(default=None)
    AddressLine4: str = field(default=None)
    AddressNumber: Any = field(default=None)
    addressType: Any = field(default=None)
    CareOf: Any = field(default=None)
    City: str = field(default=None)  # city name
    County: Any = field(default=None)
    fullAddress: Any = field(default=None)
    houseNo: Any = field(default=None)
    HouseNumber: str = field(default=None)  # house number, as a string
    HouseNumberPrefix: Any = field(default=None)
    HouseNumberSupplement: Any = field(default=None)
    inCityLimit: bool = field(
        default=None
    )  # If another city like UP, this will be false
    POBoxNumber: Any = field(default=None)
    postDirection: Any = field(default=None)
    preDirection: Any = field(default=None)
    premCode: Any = field(default=None)
    StandardAddress: str = field(default=None)  # string literal "true" or "false"
    State: str = field(default=None)  # state name
    Street: str = field(default=None)  # street name, e.g "Pacific Ave W"
    streetName: Any = field(default=None)
    streetNumber: Any = field(default=None)
    suffixCode: Any = field(default=None)
    unitInfo: Any = field(default=None)
    unitNumber: Any = field(default=None)
    unitTypeCode: Any = field(default=None)
    Zip: str = field(default=None)  # string, zip+4


@define(auto_attribs=True, slots=True, kw_only=True)
class Service(Model):
    """
    This class seems to be shared by both "services" and "servicesForGraph", though
    with different information in each. I suspect they are actually 2 spearate data
    structures, since forGraph.serviceContract corresponds to service.serviceId.
    """

    addressDetails: Any = field(default=None)
    addressInfo: Any = field(default=None)
    budgetAmount: Any = field(default=None)
    comments: Any = field(default=None)
    compoundMeter: Any = field(default=None)
    contractAccountNumber: AccountNumber = field(default=None)
    description: str = field(
        default=None
    )  # string of numbers like "123456"; some sort of id?
    eligibleInd: Any = field(default=None)
    endDate: str = field(default=None)  # YYYY-MM-DD or 9999-12-31
    enrolledInd: Any = field(default=None)
    exportMeterNum: str = field(
        default=None
    )  # string of numeric(?) id, not the same as meterNumber
    formattedBudgetAmount: Any = field(default=None)
    intervalEligibility: bool = field(default=None)
    lastname: str = field(default=None)
    latitude: str = field(default=None)
    longitude: str = field(default=None)
    meterNumber: str = field(
        default=None
    )  # string of numeric(?) id, not the same as exportMeterNum
    meterType: str = field(default=None)  # electrical: N for "net", P for "prod"
    multiplier: str = field(default=None)  # string of float? Example data is "0.0"
    netContractNum: Any = field(default=None)
    offpeakRate: Any = field(default=None)
    onpeakRate: Any = field(default=None)
    premiseId: Any = field(default=None)
    servDescr: str = field(
        default=None
    )  # copy of `description` attribute? also duplicate of exportMeterNum (with a leading space?)
    serviceCat: str = field(default=None)  # "Dev"
    serviceContract: str = field(
        default=None
    )  # links to forGraph.serviceContract to service.serviceId
    serviceDate: str = field(default=None)  # "YYYY-MM-DD HH:MM"
    serviceEndDate: str = field(
        default=None
    )  # "YYYY-MM-DD HH:MM" or "9999-12-31 00:00"
    serviceId: str = field(default=None)
    serviceNumber: str = field(default=None)  # alphanumeric id
    serviceType: str = field(default=None)  # "P" or "W" (power and water?)
    startDate: str = field(default=None)  # YYYY-MM-DD
    # grr, bug with ForwardRef https://github.com/python-attrs/cattrs/issues/206
    subMeters: "Optional[List[Service]]" = field(
        default=None
    )  # Sub-meters (e.g. a solar production meter)
    totalizerMeter: Any = field(default=None)
    uom: str = field(default=None)  # unit of measure (e.g. "CCF")

    @property
    def friendly_meter_type(self) -> str:
        """
        Just a handy property method to convert the service/meter types into
        a friendly string.
        """
        match self.serviceType:
            case "P":
                match self.meterType:
                    case "N":
                        return "Power (Net)"
                    case "P":
                        return "Power (Prod)"
                    case _:
                        raise Exception(f"unrecognized meter type: {self.meterType}")
            case "W":
                return "Water"
            case _:
                raise Exception(f"unrecognized service type: {self.serviceType}")


@define(auto_attribs=True, slots=True, kw_only=True)
class Contract(Model):
    AccountClass: Any = field(default=None)
    AccountDeterminationID: Any = field(default=None)
    BUKRS: Any = field(default=None)
    CONNECTIONOBJECT: Any = field(default=None)
    ContractAccountNumber: AccountNumber = field(default=None)
    ContractNumber: Any = field(default=None)
    Division: Any = field(default=None)
    InstallationNumber: Any = field(default=None)
    Latitude: str = field(default=None)
    Longitude: str = field(default=None)
    Meters: Any = field(default=None)
    MoveInDate: str = field(default=None)  # "YYYY-MM-DD"
    MoveOutDate: str = field(
        default=None
    )  # "YYYY-MM-DD" but if not moved out will be "9999-12-31"
    PREMISEADDRESSDETAILS: Any = field(default=None)
    PremiseNumber: Any = field(default=None)
    ServiceTypeDescription: str = field(
        default=None
    )  # "Electricity" or "Drinking Water"


@define(auto_attribs=True, slots=True, kw_only=True)
class AccountSummary(Model):
    accessType: str = field(default=None)  # "P" (for power?)
    accountNumber: AccountNumber = field(default=None)
    accountStatus: str = field(default=None)  # "A" (for active?)
    acctOffline: Any = field(default=None)
    achblocked: bool = field(default=None)  # false
    address: Address = field(default=None)
    address1: Any = field(default=None)
    addressLine1: str = field(default=None)  # "4218 JUNIPER DR W"
    addressLine2: str = field(
        default=None
    )  # some times this is the `street city` with no comma
    alert: Union[List, None] = field(default=None)  # []
    alterDueDateEligibleInd: str = field(default=None)  # "Y"
    alterDueDateInd: str = field(default=None)  # "N"
    bankDraftEligibleInd: str = field(default=None)  # "Y"
    bankDraftInd: str = field(default=None)  # "Y"
    banks: Union[List, None] = field(default=None)  # []
    billCycleCode: Any = field(default=None)
    billDate: Any = field(default=None)
    budgetBillEligibleInd: str = field(default=None)  # "N"
    budgetBillInd: str = field(default=None)  # "N",
    cashOnly: bool = field(default=None)  # false
    ccblocked: bool = field(default=None)  # false
    cisDivision: Any = field(default=None)
    collectiveParentAcctNum: Any = field(default=None)
    contracts: List[Contract] = field(factory=list)
    contributionsInd: Any = field(default=None)
    currentDueAmount: str = field(default=None)  # "0.00" or "$123.45"
    customerClass: Any = field(default=None)
    customerId: CustomerID = field(default=None)
    ebillEligibleInd: str = field(default=None)  # "Y"
    ebillEmailAddress: str = field(default=None)
    ebillInd: str = field(default=None)  # "N" or "Y"
    emailAddress: str = field(default=None)  # allcaps
    employerName: Any = field(default=None)
    firstMoveInDate: str = field(default=None)  # "YYYY-MM-DD"
    firstMoveOutDate: str = field(
        default=None
    )  # "YYYY-MM-DD" but if not moved out will be "9999-12-31"
    firstName: str = field(default=None)
    formattedMailingAddress: str = field(
        default=None
    )  # "4218 Juniper Dr W, University Place, WA 98466"
    formattedOtherAddress: Address = field(default=None)
    formattedServiceAddress: str = field(
        default=None
    )  # "4218 Juniper Dr W, University Place, WA 98466"
    fullName: str = field(default=None)  # _not_ allcaps
    hasSolidWasteContract: bool = field(default=None)  # false
    houseNo: Any = field(default=None)
    interestKey: str = field(default=None)  # "01",
    iscreditCardExpired: bool = field(default=None)  # false
    iServices: Union[List, None] = field(factory=list)
    lastIVRPaymentAmount: Any = field(default=None)
    lastName: str = field(default=None)  # allcaps
    lastPaymentAmount: str = field(default=None)  # "$123.45"
    lastPaymentAmountReceivedDate: str = field(default=None)  # "Jul 04, 2022"
    masterAccount: bool = field(default=None)  # false
    masterBillInd: Any = field(default=None)
    maxOverPayment: Any = field(default=None)
    middleName: Any = field(default=None)
    mobileServiceDD: Any = field(default=None)
    nextPPInstallAmount: str = field(default=None)  # "$0.00"
    nextPPInstallDueDate: Any = field(default=None)
    noOfScheduledPayment: Any = field(default=None)
    orgName: Any = field(default=None)
    pastDueAmount: str = field(default=None)  # "0.00" or "$0.00"
    payArrangeDownPayInd: Any = field(default=None)
    payArrangeDownpayment: Any = field(default=None)
    payArrangeEligibleInd: str = field(default=None)  # "N"
    payArrangeInd: str = field(default=None)  # "N"
    payByCheckInd: Any = field(default=None)
    payIneligibilityReason: Any = field(default=None)
    paymentDueDate: str = field(default=None)  # formatted as "Jul 04, 2022",
    paymentDueDateRaw: str = field(
        default=None
    )  # some kind of base64 encoded string containing binary data?
    paymentList: Any = field(default=None)
    paymentsAllowed: Any = field(default=None)
    payPlanStatus: Any = field(default=None)
    pendingBudgetCancellation: bool = field(default=None)  # false
    pendingNpsoInd: Any = field(default=None)
    pendingPaymentAmount: str = field(default=None)  # "$0.00"
    personId: PersonID = field(default=None)
    personType: Any = field(default=None)
    phone: Any = field(default=None)
    phoneNum: Any = field(default=None)
    phoneNumbers: Union[List, None] = field(default=None)  # []
    premiseInfo: Any = field(default=None)
    prePayEligibleInd: str = field(default=None)  # "N"
    prePayInd: str = field(default=None)  # "N"
    prevAmountdue: str = field(default=None)  # "0.00" or "$123.45"
    primaryIndividual: bool = field(default=None)  # false
    replenishAmount: Any = field(default=None)
    replenishInd: Any = field(default=None)
    replenishThreshold: Any = field(default=None)
    schedulePaymentAmount: Any = field(default=None)
    serviceAddress: str = field(
        default=None
    )  # "4218 JUNIPER DR W, UNIVERSITY PLACE, WA",
    services: List[Service] = field(
        factory=list
    )  # List all services on account
    servicesForGraph: List[Service] = field(
        factory=list
    )  # Seems maybe to list only those services that can be graphed? (helpful for us)
    subAccounts: Union[List, None] = field(default=None)  # []
    subOrdinateBillInd: Any = field(default=None)
    totalBalanceDueCents: str = field(default=None)  # "42"
    totalBalanceDueDollars: str = field(
        default=None
    )  # "-0" (yes, I had a negative balance when I pulled this)
    totalDueAmount: str = field(default=None)  # "0.00" or "-$0.42"
    unitInfo: Any = field(default=None)
    webServiceDD: Any = field(default=None)

    def get_meters(self, types: Set[str], submeters: bool = True, _submeters: List[Service] = None) -> Generator[Service,None,None]:
        services = self.servicesForGraph
        if submeters and _submeters:
            services = _submeters
        for service in services:
            # service.meterType = P or N
            # service.serviceType = P or W
            if service.serviceType in types or service.meterNumber in types:
                yield service
            if submeters and service.subMeters:
                yield from self.get_meters(types, True, _submeters=service.subMeters)


@define(auto_attribs=True, slots=True, kw_only=True)
class CheckMultipleAcctsResponse(Response):
    account: List[Account] = field(default=None)
    accSummaryTypes: List[AccountSummary] = field(default=None)


# This is used to send data to various APIs, and is part of the return value from /customer API
@define(auto_attribs=True, slots=True, kw_only=True)
class AccountContext(Model):
    access: str = field(default=None)  # "P" (power?  maybe also W for water?)
    accountAlreadyRegistrd: Any = field(default=None)
    accountHolder: str = field(default=None)  # full name
    accountNickName: str = field(default=None)
    accountNumber: AccountNumber = field(default=None)
    acctOffline: Any = field(default=None)
    acctStatus: str = field(default=None)  # "A" (for Active?)
    billCycleCode: Any = field(default=None)
    businesspartner: Any = field(default=None)
    contractaccounts: Any = field(default=None)
    contracts: Any = field(default=None)
    firstName: str = field(default=None)  # allcaps
    lastName: str = field(default=None)  # allcaps
    linkedAccounts: Any = field(default=None)
    mailingAddress: Address = field(default=None)
    masterAccount: bool = field(default=None)
    orgName: Any = field(default=None)
    personId: PersonID = field(default=None)
    phone: Any = field(default=None)
    phoneNum: Any = field(default=None)
    premiseId: Any = field(default=None)
    serviceAddress: str = field(default=None)  # full address `street, city state zip`
    serviceAddressLine1: str = field(
        default=None
    )  # first line of street address but often has house number redacted to XXXXX
    serviceAddressLine2: str = field(default=None)
    serviceCity: Any = field(default=None)  # yes, this is null in examples
    serviceId: Any = field(default=None)  # yes, this is null in examples
    serviceNumber: Any = field(default=None)
    serviceState: Any = field(default=None)
    serviceType: Any = field(default=None)
    serviceZipCode: Any = field(default=None)
    sharedAccessType: Any = field(default=None)
    sharedProfileInd: str = field(default=None)  # "N"
    subAccount: Any = field(default=None)
    summaryInd: bool = field(default=None)
    uom: str = field(default=None)  # unit of measure (e.g. "CCF")
    userID: UserID = field(default=None)
    validated: Any = field(default=None)


@define(auto_attribs=True, slots=True, kw_only=True)
class CustomerResponse(Response):
    accountContext: AccountContext
    accountSummaryType: AccountSummary = field(default=None)
    parentAcctContext: AccountContext = field(default=None)


@define(auto_attribs=True, slots=True, kw_only=True)
class Usage(Model):
    additionalInfo: str = field(
        default=None
    )  # "Test - 10.786",  # the number is scaledRead
    avgHigh: int = field(default=None)  # 0
    avgLow: int = field(default=None)  # 0
    avgMedian: int = field(default=None)  # 0
    AvgTemperature: Any = field(default=None)
    BillDays: Any = field(default=None)
    billedCharge: Any = field(default=None)
    billedConsumption: Any = field(default=None)
    billedDemandValue: float = field(default=None)  # 0.0
    billEndDate: Any = field(default=None)
    billStartDate: Any = field(default=None)
    chargeDate: Any = field(default=None)
    chargeDateRaw: Any = field(default=None)
    ContractAccountNumber: Any = field(default=None)
    ContractNumber: Any = field(default=None)
    counter: Any = field(default=None)
    daysOfService: Any = field(default=None)
    demandPeakTime: str = field(default=None)  # "2022-07-17 21:00",
    Division: Any = field(default=None)
    estimatedRead: Any = field(default=None)
    FromDate: Any = field(default=None)
    gallonsConsumption: Any = field(default=None)
    intervalread: Any = field(default=None)
    intervalType: Any = field(default=None)
    invoiceDate: Any = field(default=None)
    kVar: Any = field(default=None)
    kVArh: Any = field(default=None)
    kVarhReceivedValue: Any = field(default=None)
    lowConsumpUsage: Any = field(default=None)
    meterNumber: Any = field(default=None)
    meterSN: Any = field(default=None)
    multipler: Any = field(default=None)
    netReceivedCategory: Any = field(default=None)
    netReceivedValue: Any = field(default=None)
    netValue: Any = field(default=None)
    port: Any = field(default=None)
    powerFactor: Any = field(default=None)
    projectedCons: Any = field(default=None)
    rawConsumption: Any = field(default=None)
    readDate: str = field(default=None)  # "2022-07-17",
    readDateTime: Any = field(default=None)
    receivedRegisterRead: Any = field(default=None)
    scaledRead: float = field(
        default=None
    )  # 10.786,  # ever-increasing, doesn't seem to correlate to  usageConsumptionValue
    serviceType: Any = field(default=None)
    temp: int = field(default=None)  # 0
    tempHigh: int = field(default=None)  # 0
    tempLow: int = field(default=None)  # 0
    ToDate: Any = field(default=None)
    uom: str = field(default=None)  # "CCF" (cubic feet)
    usageCategory: str = field(default=None)  # D for "daily"?
    usageConsumptionValue: float = field(default=None)  # 1.892
    usageDate: str = field(default=None)  # "2022-07-17",
    usageDemandValue: float = field(default=None)  # 0.0
    usageHighTemp: float = field(default=None)  # 0.0
    usageLowTemp: float = field(default=None)  # 0.0


@define(auto_attribs=True, slots=True, kw_only=True)
class UsageResponse(Response):
    billedHistory: Union[List, None] = field(default=None)
    commercial: str = field(default=None)  # "N" or "Y" (solar net meter seems to get Y)
    history: List[Usage] = field(factory=list)
