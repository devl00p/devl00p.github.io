---
title: "Writeup for Huntress 2023 M Three Sixty Five challenges (Azure AD)"
tags: [CTF, Huntress 2023]
---

## Description

> For this challenge, you can connect into a PowerShell Core instance. Note that this is running out of a Linux-based Docker container, so you do not have a full-blown Windows operating system or pure PowerShell.
> 
> When you connect to the session for the very first time, you will be authenticated into a Microsoft 365 environment. WARNING: Once you disconnect, you will need to restart your container to reauthenticate
> 
> For all of the M365-related challenges, you can use this same container for all the associated tasks in this group. If your container does not seem to be able to authenticate, please wait some time -- perhaps Microsoft might not like multiple logins at the same time ;)

## Solutions

We had to reply to 4 questions to obtain as many flag.

Once connected we have access to a Powershell prompt and the module [AADInternals](https://aadinternals.com/aadinternals/) is already loaded.

The server is using the cloud-based Active Directory : Azure AD.

The powershell module AADInternals is described this way:

> AADInternals toolkit is a PowerShell module containing tools for administering and hacking Azure AD and Office 365. It is listed in MITRE ATT&CK with id S0677.

### Welcome to our hackable M365 tenant! Can you find any juicy details, like perhaps the street address this organization is associated with?

We just have to search for something useful in the AADInternals documentation and use it:

```console
PS /home/user> Get-AADIntTenantDetails

odata.type                                : Microsoft.DirectoryServices.TenantDetail
objectType                                : Company
objectId                                  : 05985beb-42bc-4c24-bf49-c1730a825406
deletionTimestamp                         : 
assignedPlans                             : {@{assignedTimestamp=09/16/2023 06:40:21; capabilityStatus=Enabled; service=exchange; servicePlanId=9f431833-0334-42de-a7dc-70aa40db46db}, @{assignedTimestamp=09/16/
                                            2023 06:40:21; capabilityStatus=Enabled; service=exchange; servicePlanId=5136a095-5cf0-4aff-bec3-e84448b38ea5}, @{assignedTimestamp=09/16/2023 06:40:17; capabilitySt
                                            atus=Enabled; service=M365LabelAnalytics; servicePlanId=d9fa6af4-e046-4c89-9226-729a0786685d}, @{assignedTimestamp=09/16/2023 06:40:19; capabilityStatus=Enabled; ser
                                            vice=MicrosoftCommunicationsOnline; servicePlanId=0feaeb32-d00e-4d66-bd5a-43b5b83db82c}…}
authorizedServiceInstance                 : {exchange/namprd04-012-01, ccibotsprod/NA001, YammerEnterprise/NA030, WhiteboardServices/NA001…}
city                                      : Ellicott City
cloudRtcUserPolicies                      : 
companyLastDirSyncTime                    : 
companyTags                               : {o365.microsoft.com/startdate=638304432108764015, azure.microsoft.com/developer365=active, o365.microsoft.com/version=15, o365.microsoft.com/signupexperience=GeminiS
                                            ignUpUI}
compassEnabled                            : 
country                                   : 
countryLetterCode                         : US
dirSyncEnabled                            : 
displayName                               : HuntressCTF
isMultipleDataLocationsForServicesEnabled : 
marketingNotificationEmails               : {}
postalCode                                : 21043
preferredLanguage                         : en
privacyProfile                            : 
provisionedPlans                          : {@{capabilityStatus=Enabled; provisioningStatus=Success; service=exchange}, @{capabilityStatus=Enabled; provisioningStatus=Success; service=exchange}, @{capabilitySt
                                            atus=Enabled; provisioningStatus=Success; service=exchange}, @{capabilityStatus=Enabled; provisioningStatus=Success; service=exchange}…}
provisioningErrors                        : {}
releaseTrack                              : 
replicationScope                          : NA
securityComplianceNotificationMails       : {}
securityComplianceNotificationPhones      : {}
selfServePasswordResetPolicy              : 
state                                     : MD
street                                    : flag{dd7bf230fde8d4836917806aff6a6b27}
technicalNotificationMails                : {huntressctf@outlook.com}
telephoneNumber                           : 8005555555
tenantType                                : 
createdDateTime                           : 09/16/2023 06:40:09
verifiedDomains                           : {@{capabilities=Email, OfficeCommunicationsOnline; default=True; id=000520000FC960F2; initial=True; name=4rhdc6.onmicrosoft.com; type=Managed}}
windowsCredentialsEncryptionCertificate   :
```

### This tenant looks to have some odd Conditional Access Policies. Can you find a weird one?

{% raw %}
```console
PS /home/user> Get-AADIntConditionalAccessPolicies

odata.type          : Microsoft.DirectoryServices.Policy
objectType          : Policy
objectId            : 668225f8-1b04-4c50-ad93-a96234c9e630
deletionTimestamp   :
displayName         : flag{d02fd5f79caa273ea535a526562fd5f7}
keyCredentials      : {}
policyType          : 18
policyDetail        : {{"Version":1,"CreatedDateTime":"2023-10-16T15:23:45.8269524Z","ModifiedDateTime":"2023-10-16T15:38:14.8630673Z","State":"Enabled","Conditions":{"Applications":{"Include":[{"Applications"
                      :["None"]}]},"Users":{"Include":[{"Users":["None"]}]}},"Controls":[{"Control":["Mfa"]}],"EnforceAllPoliciesForEas":true,"IncludeOtherLegacyClientTypeForEvaluation":true}}
policyIdentifier    :
tenantDefaultPolicy :

odata.type          : Microsoft.DirectoryServices.Policy
objectType          : Policy
objectId            : 781fecfa-78c7-41b3-9961-fd82132465e3
deletionTimestamp   :
displayName         : Default Policy
keyCredentials      : {}
policyType          : 18
policyDetail        : {{"Version":0,"State":"Disabled"}}
policyIdentifier    : 10/16/2023 15:38:15
tenantDefaultPolicy : 18
```
{% endraw %}

### We observed saw some sensitive information being shared over a Microsoft Teams message! Can you track it down?

```console
PS /home/user> Get-AADIntTeamsMessages

ClientMessageId : 8803098928400015000
Id              : 1695838171758
MessageType     : Text
DisplayName     : FNU LNU
ArrivalTime     : 09/27/2023 18:09:31
DeletionTime    :
Link            : 19:8tLE5Hp0MfXN3KZ3gBdcGMUs3Td78d3i5uk6uSC9rE81@thread.tacv2
Content         : flag{f17cf5c1e2e94ddb62b98af0fbbd46e1}
Type            : Message

ClientMessageId : 8803098928400015000
Id              : 1695838171758
MessageType     : Text
DisplayName     : FNU LNU
ArrivalTime     : 09/27/2023 18:09:31
DeletionTime    :
Link            : 19:8tLE5Hp0MfXN3KZ3gBdcGMUs3Td78d3i5uk6uSC9rE81@thread.tacv2
Content         : flag{f17cf5c1e2e94ddb62b98af0fbbd46e1}
Type            : Message
```

### One of the users in this environment seems to have unintentionally left some information in their account details. Can you track down The President?

I dumped all users and use a `grep`:

```console
PS /home/user> Get-AADIntUsers | grep 'flag{'                    
PhoneNumber                            : flag{1e674f0dd1434f2bb3fe5d645b0f9cc3}
```
