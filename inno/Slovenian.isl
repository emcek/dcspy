; *** Inno Setup version 6.4.0+ Slovenian messages ***
;
; To download user-contributed translations of this file, go to:
;   http://www.jrsoftware.org/is3rdparty.php
;
; Note: When translating this text, do not add periods (.) to the end of
; messages that didn't have them already, because on those messages Inno
; Setup adds the periods automatically (appending a period would result in
; two periods being displayed).
;
; Maintained by Jernej Simoncic (jernej+s-innosetup@eternallybored.org)

[LangOptions]
LanguageName=Slovenski
LanguageID=$0424
LanguageCodePage=1250

DialogFontName=
[Messages]

; *** Application titles
SetupAppTitle=Namestitev
SetupWindowTitle=Namestitev - %1
UninstallAppTitle=Odstranitev
UninstallAppFullTitle=Odstranitev programa %1

; *** Misc. common
InformationTitle=Informacija
ConfirmTitle=Potrditev
ErrorTitle=Napaka

; *** SetupLdr messages
SetupLdrStartupMessage=V ra�unalnik boste namestili program %1. �elite nadaljevati?
LdrCannotCreateTemp=Ni bilo mogo�e ustvariti za�asne datoteke. Namestitev je prekinjena
LdrCannotExecTemp=Ni bilo mogo�e zagnati datoteke v za�asni mapi. Namestitev je prekinjena

; *** Startup error messages
LastErrorMessage=%1.%n%nNapaka %2: %3
SetupFileMissing=Datoteka %1 manjka. Odpravite napako ali si priskrbite drugo kopijo programa.
SetupFileCorrupt=Datoteke namestitvenega programa so okvarjene. Priskrbite si drugo kopijo programa.
SetupFileCorruptOrWrongVer=Datoteke so okvarjene ali nezdru�ljive s to razli�ico namestitvenega programa. Odpravite napako ali si priskrbite drugo kopijo programa.
InvalidParameter=Naveden je bil napa�en parameter ukazne vrstice:%n%n%1
SetupAlreadyRunning=Namestitveni program se �e izvaja.
WindowsVersionNotSupported=Program ne deluje na va�i razli�ici sistema Windows.
WindowsServicePackRequired=Program potrebuje %1 s servisnim paketom %2 ali novej�o razli�ico.
NotOnThisPlatform=Program ni namenjen za uporabo v %1.
OnlyOnThisPlatform=Program je namenjen le za uporabo v %1.
OnlyOnTheseArchitectures=Program lahko namestite le na Windows sistemih, na naslednjih vrstah procesorjev:%n%n%1
WinVersionTooLowError=Ta program zahteva %1 razli�ico %2 ali novej�o.
WinVersionTooHighError=Tega programa ne morete namestiti v %1 razli�ice %2 ali novej�e.
AdminPrivilegesRequired=Za namestitev programa morate biti prijavljeni v ra�un s skrbni�kimi pravicami.
PowerUserPrivilegesRequired=Za namestitev programa morate biti prijavljeni v ra�un s skrbni�kimi ali power user pravicami.
SetupAppRunningError=Program %1 je trenutno odprt.%n%nZaprite program, nato kliknite V redu za nadaljevanje ali Prekli�i za izhod.
UninstallAppRunningError=Program %1 je trenutno odprt.%n%nZaprite program, nato kliknite V redu za nadaljevanje ali Prekli�i za izhod.

; *** Startup questions
PrivilegesRequiredOverrideTitle=Izberite na�in namestitve
PrivilegesRequiredOverrideInstruction=Izberite na�in namestitve
PrivilegesRequiredOverrideText1=Program %1 lahko namestite za vse uporabnike (potrebujete skrbni�ke pravice), ali pa samo za vas.
PrivilegesRequiredOverrideText2=Program %1 lahko namestite samo za vas, ali pa za vse uporabnike (potrebujete skrbni�ke pravice).
PrivilegesRequiredOverrideAllUsers=N&amesti za vse uporabnike
PrivilegesRequiredOverrideAllUsersRecommended=N&amesti za vse uporabnike (priporo�eno)
PrivilegesRequiredOverrideCurrentUser=Namesti samo za&me
PrivilegesRequiredOverrideCurrentUserRecommended=Namesti samo za&me (priporo�eno)

; *** Misc. errors
ErrorCreatingDir=Namestitveni program ni mogel ustvariti mape �%1�
ErrorTooManyFilesInDir=Namestitveni program ne more ustvariti nove datoteke v mapi �%1�, ker vsebuje preve� datotek

; *** Setup common messages
ExitSetupTitle=Prekini namestitev
ExitSetupMessage=Namestitev ni kon�ana. �e jo boste prekinili, program ne bo name��en.%n%nPonovno namestitev lahko izvedete kasneje.%n%n�elite prekiniti namestitev?
AboutSetupMenuItem=&O namestitvenem programu...
AboutSetupTitle=O namestitvenem programu
AboutSetupMessage=%1 razli�ica %2%n%3%n%n%1 doma�a stran:%n%4
AboutSetupNote=
TranslatorNote=Slovenski prevod:%nMiha Remec%nJernej Simon�i� <jernej|s-innosetup@eternallybored.org>

; *** Buttons
ButtonBack=< Na&zaj
ButtonNext=&Naprej >
ButtonInstall=&Namesti
ButtonOK=V redu
ButtonCancel=Prekli�i
ButtonYes=&Da
ButtonYesToAll=Da za &vse
ButtonNo=&Ne
ButtonNoToAll=N&e za vse
ButtonFinish=&Kon�aj
ButtonBrowse=Pre&brskaj...
ButtonWizardBrowse=Pre&brskaj...
ButtonNewFolder=&Ustvari novo mapo

; *** "Select Language" dialog messages
SelectLanguageTitle=Izbira jezika namestitve
SelectLanguageLabel=Izberite jezik, ki ga �elite uporabljati med namestitvijo.

; *** Common wizard text
ClickNext=Kliknite Naprej za nadaljevanje namestitve ali Prekli�i za prekinitev namestitve.
BeveledLabel=
BrowseDialogTitle=Izbira mape
BrowseDialogLabel=Izberite mapo s spiska, nato kliknite V redu.
NewFolderName=Nova mapa

; *** "Welcome" wizard page
WelcomeLabel1=Dobrodo�li v namestitev programa [name].
WelcomeLabel2=V ra�unalnik boste namestili program [name/ver].%n%nPriporo�ljivo je, da pred za�etkom namestitve zaprete vse odprte programe.

; *** "License Agreement" wizard page
WizardLicense=Licen�na pogodba
LicenseLabel=Pred nadaljevanjem preberite licen�no pogodbo za uporabo programa.
LicenseLabel3=Preberite licen�no pogodbo za uporabo programa. Program lahko namestite le, �e se s pogodbo v celoti strinjate.
LicenseAccepted=&Da, sprejemam vse pogoje licen�ne pogodbe
LicenseNotAccepted=N&e, pogojev licen�ne pogodbe ne sprejmem

; *** "Information" wizard pages
WizardInfoBefore=Informacije
InfoBeforeLabel=Pred nadaljevanjem preberite naslednje pomembne informacije.
InfoBeforeClickLabel=Ko boste pripravljeni na nadaljevanje namestitve, kliknite Naprej.
WizardInfoAfter=Informacije
InfoAfterLabel=Pred nadaljevanjem preberite naslednje pomembne informacije.
InfoAfterClickLabel=Ko boste pripravljeni na nadaljevanje namestitve, kliknite Naprej.

; *** "User Information" wizard page
WizardUserInfo=Podatki o uporabniku
UserInfoDesc=Vnesite svoje podatke.
UserInfoName=&Ime:
UserInfoOrg=&Podjetje:
UserInfoSerial=&Serijska �tevilka:
UserInfoNameRequired=Vnos imena je obvezen.

; *** "Select Destination Location" wizard page
WizardSelectDir=Izbira ciljnega mesta
SelectDirDesc=Kam �elite namestiti program [name]?
SelectDirLabel3=Program [name] bo name��en v naslednjo mapo.
SelectDirBrowseLabel=Za nadaljevanje kliknite Naprej. �e �elite izbrati drugo mapo, kliknite Prebrskaj.
DiskSpaceGBLabel=Na disku mora biti vsaj [gb] GB prostora.
DiskSpaceMBLabel=Na disku mora biti vsaj [mb] MB prostora.
CannotInstallToNetworkDrive=Programa ni mogo�e namestiti na mre�ni pogon.
CannotInstallToUNCPath=Programa ni mogo�e namestiti v UNC pot.
InvalidPath=Vpisati morate polno pot vklju�no z oznako pogona. Primer:%n%nC:\PROGRAM%n%nali UNC pot v obliki:%n%n\\stre�nik\mapa_skupne_rabe
InvalidDrive=Izbrani pogon ali omre�no sredstvo UNC ne obstaja ali ni dostopno. Izberite drugega.
DiskSpaceWarningTitle=Na disku ni dovolj prostora
DiskSpaceWarning=Namestitev potrebuje vsaj %1 KB prostora, toda na izbranem pogonu je na voljo le %2 KB.%n%n�elite kljub temu nadaljevati?
DirNameTooLong=Ime mape ali poti je predolgo.
InvalidDirName=Ime mape ni veljavno.
BadDirName32=Ime mape ne sme vsebovati naslednjih znakov:%n%n%1
DirExistsTitle=Mapa �e obstaja
DirExists=Mapa%n%n%1%n%n�e obstaja. �elite program vseeno namestiti v to mapo?
DirDoesntExistTitle=Mapa ne obstaja
DirDoesntExist=Mapa %n%n%1%n%nne obstaja. Ali jo �elite ustvariti?

; *** "Select Components" wizard page
WizardSelectComponents=Izbira komponent
SelectComponentsDesc=Katere komponente �elite namestiti?
SelectComponentsLabel2=Ozna�ite komponente, ki jih �elite namestiti; odzna�ite komponente, ki jih ne �elite namestiti. Kliknite Naprej, ko boste pripravljeni za nadaljevanje.
FullInstallation=Popolna namestitev
; if possible don't translate 'Compact' as 'Minimal' (I mean 'Minimal' in your language)
CompactInstallation=Osnovna namestitev
CustomInstallation=Namestitev po meri
NoUninstallWarningTitle=Komponente �e obstajajo
NoUninstallWarning=Namestitveni program je ugotovil, da so naslednje komponente �e name��ene v ra�unalniku:%n%n%1%n%nNamestitveni program teh �e name��enih komponent ne bo odstranil.%n%n�elite vseeno nadaljevati?
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceGBLabel=Za izbrano namestitev potrebujete vsaj [gb] GB prostora na disku.
ComponentsDiskSpaceMBLabel=Za izbrano namestitev potrebujete vsaj [mb] MB prostora na disku.

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=Izbira dodatnih opravil
SelectTasksDesc=Katera dodatna opravila �elite izvesti?
SelectTasksLabel2=Izberite dodatna opravila, ki jih bo namestitveni program opravil med namestitvijo programa [name], nato kliknite Naprej.

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=Izbira mape v meniju �Za�etek�
SelectStartMenuFolderDesc=Kje naj namestitveni program ustvari bli�njice?
SelectStartMenuFolderLabel3=Namestitveni program bo ustvaril bli�njice v naslednji mapi v meniju �Start�.
SelectStartMenuFolderBrowseLabel=Za nadaljevanje kliknite Naprej. �e �elite izbrati drugo mapo, kliknite Prebrskaj.
MustEnterGroupName=Ime skupine mora biti vpisano.
GroupNameTooLong=Ime mape ali poti je predolgo.
InvalidGroupName=Ime mape ni veljavno.
BadGroupName=Ime skupine ne sme vsebovati naslednjih znakov:%n%n%1
NoProgramGroupCheck2=&Ne ustvari mape v meniju �Start�

; *** "Ready to Install" wizard page
WizardReady=Pripravljen za namestitev
ReadyLabel1=Namestitveni program je pripravljen za namestitev programa [name] v va� ra�unalnik.
ReadyLabel2a=Kliknite Namesti za za�etek name��anja. Kliknite Nazaj, �e �elite pregledati ali spremeniti katerokoli nastavitev.
ReadyLabel2b=Kliknite Namesti za za�etek name��anja.
ReadyMemoUserInfo=Podatki o uporabniku:
ReadyMemoDir=Ciljno mesto:
ReadyMemoType=Vrsta namestitve:
ReadyMemoComponents=Izbrane komponente:
ReadyMemoGroup=Mapa v meniju �Za�etek�:
ReadyMemoTasks=Dodatna opravila:

; *** TDownloadWizardPage wizard page and DownloadTemporaryFile
DownloadingLabel=Prena�am dodatne datoteke...
ButtonStopDownload=Prekini preno&s
StopDownload=Ali res �elite prekiniti prenos?
ErrorDownloadAborted=Prenos prekinjen
ErrorDownloadFailed=Prenos ni uspel: %1 %2
ErrorDownloadSizeFailed=Pridobivanje velikosti ni uspelo: %1 %2
ErrorFileHash1=Pridobivanje zgo��ene vrednosti ni uspelo: %1
ErrorFileHash2=Neveljavna zgo��ena vrednost: pri�akovana %1, dobljena %2
ErrorProgress=Neveljaven potek: %1 od %2
ErrorFileSize=Neveljavna velikost datoteke: pri�akovana %1, dobljena %2

; *** TExtractionWizardPage wizard page and Extract7ZipArchive
ExtractionLabel=Raz�irjanje dodatnih datotek...
ButtonStopExtraction=U&stavi raz�irjanje
StopExtraction=Ste prepri�ani, da �elite ustaviti raz�irjanje datotek?
ErrorExtractionAborted=Raz�irjanje datotek prekinjeno
ErrorExtractionFailed=Napaka pri raz�irjanju: %1

; *** "Preparing to Install" wizard page
WizardPreparing=Pripravljam za namestitev
PreparingDesc=Namestitveni program je pripravljen za namestitev programa [name] v va� ra�unalnik.
PreviousInstallNotCompleted=Namestitev ali odstranitev prej�njega programa ni bila kon�ana. Da bi jo dokon�ali, morate ra�unalnik znova zagnati.%n%nPo ponovnem zagonu ra�unalnika znova za�enite namestitveni program, da boste kon�ali namestitev programa [name].
CannotContinue=Namestitveni program ne more nadaljevati. Pritisnite Prekli�i za izhod.

; *** "Installing" wizard page
ApplicationsFound=Naslednji programi uporabljajo datoteke, ki jih mora namestitveni program posodobiti. Priporo�ljivo je, da namestitvenemu programu dovolite, da te programe kon�a.
ApplicationsFound2=Naslednji programi uporabljajo datoteke, ki jih mora namestitveni program posodobiti. Priporo�ljivo je, da namestitvenemu programu dovolite, da te programe kon�a. Po koncu namestitve bo namestitveni program poizkusil znova zagnati te programe.
CloseApplications=S&amodejno zapri programe
DontCloseApplications=&Ne zapri programov
ErrorCloseApplications=Namestitvenemu programu ni uspelo samodejno zapreti vseh programov. Priporo�ljivo je, da pred nadaljevanjem zaprete vse programe, ki uporabljajo datoteke, katere mora namestitev posodobiti.
PrepareToInstallNeedsRestart=Namestitveni program mora znova zagnati va� ra�unalnik. Za dokon�anje namestitve programa [name], po ponovnem zagonu znova za�enite namestitveni program.%n%nAli �elite zdaj znova zagnati ra�unalnik?

WizardInstalling=Name��anje
InstallingLabel=Po�akajte, da bo program [name] name��en v va� ra�unalnik.

; *** "Setup Completed" wizard page
FinishedHeadingLabel=Zaklju�ek namestitve programa [name]
FinishedLabelNoIcons=Program [name] je name��en v va� ra�unalnik.
FinishedLabel=Program [name] je name��en v va� ra�unalnik. Program za�enete tako, da odprete pravkar ustvarjene programske ikone.
ClickFinish=Kliknite tipko Kon�aj za zaklju�ek namestitve.
FinishedRestartLabel=Za dokon�anje namestitve programa [name] morate ra�unalnik znova zagnati. Ali ga �elite znova zagnati zdaj?
FinishedRestartMessage=Za dokon�anje namestitve programa [name] morate ra�unalnik znova zagnati. %n%nAli ga �elite znova zagnati zdaj?
ShowReadmeCheck=�elim prebrati datoteko BERIME
YesRadio=&Da, ra�unalnik znova za�eni zdaj
NoRadio=&Ne, ra�unalnik bom znova zagnal pozneje

; used for example as 'Run MyProg.exe'
RunEntryExec=Za�eni %1
; used for example as 'View Readme.txt'
RunEntryShellExec=Preglej %1

; *** "Setup Needs the Next Disk" stuff
ChangeDiskTitle=Namestitveni program potrebuje naslednji disk
SelectDiskLabel2=Vstavite disk %1 in kliknite V redu.%n%n�e se datoteke s tega diska nahajajo v drugi mapi kot je navedena spodaj, vnesite pravilno pot ali kliknite Prebrskaj.
PathLabel=&Pot:
FileNotInDir2=Datoteke �%1� ni v mapi �%2�. Vstavite pravilni disk ali izberite drugo mapo.
SelectDirectoryLabel=Vnesite mesto naslednjega diska.

; *** Installation phase messages
SetupAborted=Namestitev ni bila kon�ana.%n%nOdpravite te�avo in znova odprite namestitveni program.
AbortRetryIgnoreSelectAction=Izberite dejanje
AbortRetryIgnoreRetry=Poizkusi &znova
AbortRetryIgnoreIgnore=&Prezri napako in nadaljuj
AbortRetryIgnoreCancel=Prekli�i namestitev

; *** Installation status messages
StatusClosingApplications=Zapiranje programov...
StatusCreateDirs=Ustvarjanje map...
StatusExtractFiles=Raz�irjanje datotek...
StatusCreateIcons=Ustvarjanje bli�njic...
StatusCreateIniEntries=Vpisovanje v INI datoteke...
StatusCreateRegistryEntries=Ustvarjanje vnosov v register...
StatusRegisterFiles=Registriranje datotek...
StatusSavingUninstall=Zapisovanje podatkov za odstranitev...
StatusRunProgram=Zaklju�evanje namestitve...
StatusRestartingApplications=Zaganjanje programov...
StatusRollback=Obnavljanje prvotnega stanja...

; *** Misc. errors
ErrorInternal2=Interna napaka: %1
ErrorFunctionFailedNoCode=%1 ni uspel(a)
ErrorFunctionFailed=%1 ni uspel(a); koda %2
ErrorFunctionFailedWithMessage=%1 ni uspela; koda %2.%n%3
ErrorExecutingProgram=Ne morem zagnati programa:%n%1

; *** Registry errors
ErrorRegOpenKey=Napaka pri odpiranju klju�a v registru:%n%1\%2
ErrorRegCreateKey=Napaka pri ustvarjanju klju�a v registru:%n%1\%2
ErrorRegWriteKey=Napaka pri pisanju klju�a v registru:%n%1\%2

; *** INI errors
ErrorIniEntry=Napaka pri vpisu v INI datoteko �%1�.

; *** File copying errors
FileAbortRetryIgnoreSkipNotRecommended=Pre&sko�i to datoteko (ni priporo�eno)
FileAbortRetryIgnoreIgnoreNotRecommended=Prezr&i napako in nadaljuj (ni priporo�eno)
SourceIsCorrupted=Izvorna datoteka je okvarjena
SourceDoesntExist=Izvorna datoteka �%1� ne obstaja
ExistingFileReadOnly2=Obstoje�e datoteke ni mogo�e nadomestiti, ker ima oznako samo za branje.
ExistingFileReadOnlyRetry=Odst&rani oznako samo za branje in poizkusi ponovno
ExistingFileReadOnlyKeepExisting=&Ohrani obstoje�o datoteko
ErrorReadingExistingDest=Pri branju obstoje�e datoteke je pri�lo do napake:
FileExistsSelectAction=Izberite dejanje
FileExists2=Datoteka �e obstaja.
FileExistsOverwriteExisting=&Prepi�i obstoje�o datoteko
FileExistsKeepExisting=&Ohrani trenutno datoteko
FileExistsOverwriteOrKeepAll=&To naredite za preostale spore
ExistingFileNewerSelectAction=Izberite dejanje
ExistingFileNewer2=Obstoje�a datoteka je novej�a, kot datoteka, ki se name��a.
ExistingFileNewerOverwriteExisting=&Prepi�i obstoje�o datoteko
ExistingFileNewerKeepExisting=&Ohrani trenutno datoteko (priporo�eno)
ExistingFileNewerOverwriteOrKeepAll=&To naredite za preostale spore
ErrorChangingAttr=Pri poskusu spremembe lastnosti datoteke je pri�lo do napake:
ErrorCreatingTemp=Pri ustvarjanju datoteke v ciljni mapi je pri�lo do napake:
ErrorReadingSource=Pri branju izvorne datoteke je pri�lo do napake:
ErrorCopying=Pri kopiranju datoteke je pri�lo do napake:
ErrorReplacingExistingFile=Pri poskusu zamenjave obstoje�e datoteke je pri�lo do napake:
ErrorRestartReplace=Napaka RestartReplace:
ErrorRenamingTemp=Pri poskusu preimenovanja datoteke v ciljni mapi je pri�lo do napake:
ErrorRegisterServer=Registracija DLL/OCX ni uspela: %1
ErrorRegSvr32Failed=RegSvr32 ni uspel s kodo napake %1
ErrorRegisterTypeLib=Registracija TypeLib ni uspela: %1

; *** Uninstall display name markings
UninstallDisplayNameMark=%1 (%2)
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32-bitno
UninstallDisplayNameMark64Bit=64-bitno
UninstallDisplayNameMarkAllUsers=vsi uporabniki
UninstallDisplayNameMarkCurrentUser=trenutni uporabnik

; *** Post-installation errors
ErrorOpeningReadme=Pri odpiranju datoteke BERIME je pri�lo do napake.
ErrorRestartingComputer=Namestitvenemu programu ni uspelo znova zagnati ra�unalnika. Sami znova za�enite ra�unalnik.

; *** Uninstaller messages
UninstallNotFound=Datoteka �%1� ne obstaja. Odstranitev ni mogo�a.
UninstallOpenError=Datoteke �%1� ne morem odpreti. Ne morem odstraniti
UninstallUnsupportedVer=Dnevni�ka datoteka �%1� je v obliki, ki je ta razli�ica odstranitvenega programa ne razume. Programa ni mogo�e odstraniti
UninstallUnknownEntry=V dnevni�ki datoteki je bil najden neznani vpis (%1)
ConfirmUninstall=Ste prepri�ani, da �elite v celoti odstraniti program %1 in pripadajo�e komponente?
UninstallOnlyOnWin64=To namestitev je mogo�e odstraniti le v 64-bitni razli�ici sistema Windows.
OnlyAdminCanUninstall=Za odstranitev tega programa morate imeti skrbni�ke pravice.
UninstallStatusLabel=Po�akajte, da se program %1 odstrani iz va�ega ra�unalnika.
UninstalledAll=Program %1 je bil uspe�no odstranjen iz va�ega ra�unalnika.
UninstalledMost=Odstranjevanje programa %1 je kon�ano.%n%nNekatere datoteke niso bile odstranjene in jih lahko odstranite ro�no.
UninstalledAndNeedsRestart=Za dokon�anje odstranitve programa %1 morate ra�unalnik znova zagnati.%n%nAli ga �elite znova zagnati zdaj?
UninstallDataCorrupted=Datoteka �%1� je okvarjena. Odstranitev ni mo�na

; *** Uninstallation phase messages
ConfirmDeleteSharedFileTitle=�elite odstraniti datoteko v skupni rabi?
ConfirmDeleteSharedFile2=Spodaj izpisane datoteke v skupni rabi ne uporablja ve� noben program. �elite odstraniti to datoteko?%n%n�e jo uporablja katerikoli program in jo boste odstranili, ta program verjetno ne bo ve� deloval pravilno. �e niste prepri�ani, kliknite Ne. �e boste datoteko ohranili v ra�unalniku, ne bo ni� narobe.
SharedFileNameLabel=Ime datoteke:
SharedFileLocationLabel=Mesto:
WizardUninstalling=Odstranjevanje programa
StatusUninstalling=Odstranjujem %1...

ShutdownBlockReasonInstallingApp=Name��am %1.
ShutdownBlockReasonUninstallingApp=Odstranjujem %1.

[CustomMessages]

NameAndVersion=%1 razli�ica %2
AdditionalIcons=Dodatne ikone:
CreateDesktopIcon=Ustvari ikono na &namizju
CreateQuickLaunchIcon=Ustvari ikono za &hitri zagon
ProgramOnTheWeb=%1 na spletu
UninstallProgram=Odstrani %1
LaunchProgram=Odpri %1
AssocFileExtension=&Pove�i %1 s pripono %2
AssocingFileExtension=Povezujem %1 s pripono %2...
AutoStartProgramGroupDescription=Zagon:
AutoStartProgram=Samodejno za�eni %1
AddonHostProgramNotFound=Programa %1 ni bilo mogo�e najti v izbrani mapi.%n%nAli �elite vseeno nadaljevati?
