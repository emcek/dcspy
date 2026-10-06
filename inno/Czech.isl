; *******************************************************
; ***                                                 ***
; *** Inno Setup version 6.4.0+ Czech messages        ***
; ***                                                 ***
; *** Original Author:                                ***
; ***                                                 ***
; ***   Ivo Bauer (bauer@ozm.cz)                      ***
; ***                                                 ***
; *** Contributors:                                   ***
; ***                                                 ***
; ***   Lubos Stanek (lubek@users.sourceforge.net)    ***
; ***   Vitezslav Svejdar (vitezslav.svejdar@cuni.cz) ***
; ***   Jiri Fenz (jirifenz@gmail.com)                ***
; ***                                                 ***
; *******************************************************

[LangOptions]
LanguageName=<010C>e<0161>tina
LanguageID=$0405
LanguageCodePage=1250

[Messages]

; *** Application titles
SetupAppTitle=Pr�vodce instalac�
SetupWindowTitle=Pr�vodce instalac� - %1
UninstallAppTitle=Pr�vodce odinstalac�
UninstallAppFullTitle=Pr�vodce odinstalac� - %1

; *** Misc. common
InformationTitle=Informace
ConfirmTitle=Potvrzen�
ErrorTitle=Chyba

; *** SetupLdr messages
SetupLdrStartupMessage=V�t� V�s pr�vodce instalac� produktu %1. Chcete pokra�ovat?
LdrCannotCreateTemp=Nelze vytvo�it do�asn� soubor. Pr�vodce instalac� bude ukon�en
LdrCannotExecTemp=Nelze spustit soubor v do�asn� slo�ce. Pr�vodce instalac� bude ukon�en
HelpTextNote=

; *** Startup error messages
LastErrorMessage=%1.%n%nChyba %2: %3
SetupFileMissing=Instala�n� slo�ka neobsahuje soubor %1. Opravte pros�m tuto chybu nebo si opat�ete novou kopii tohoto produktu.
SetupFileCorrupt=Soubory pr�vodce instalac� jsou po�kozeny. Opat�ete si pros�m novou kopii tohoto produktu.
SetupFileCorruptOrWrongVer=Soubory pr�vodce instalac� jsou po�kozeny nebo se neslu�uj� s touto verz� pr�vodce instalac�. Opravte pros�m tuto chybu nebo si opat�ete novou kopii tohoto produktu.
InvalidParameter=P��kazov� ��dek obsahuje neplatn� parametr:%n%n%1
SetupAlreadyRunning=Pr�vodce instalac� je ji� spu�t�n.
WindowsVersionNotSupported=Tento produkt nepodporuje verzi MS Windows, kter� b�� na Va�em po��ta�i.
WindowsServicePackRequired=Tento produkt vy�aduje %1 Service Pack %2 nebo vy���.
NotOnThisPlatform=Tento produkt nelze spustit ve %1.
OnlyOnThisPlatform=Tento produkt mus� b�t spu�t�n ve %1.
OnlyOnTheseArchitectures=Tento produkt lze nainstalovat pouze ve verz�ch MS Windows s podporou architektury procesor�:%n%n%1
WinVersionTooLowError=Tento produkt vy�aduje %1 verzi %2 nebo vy���.
WinVersionTooHighError=Tento produkt nelze nainstalovat ve %1 verzi %2 nebo vy���.
AdminPrivilegesRequired=K instalaci tohoto produktu mus�te b�t p�ihl�eni s opr�vn�n�mi spr�vce.
PowerUserPrivilegesRequired=K instalaci tohoto produktu mus�te b�t p�ihl�eni s opr�vn�n�mi spr�vce nebo �lena skupiny Power Users.
SetupAppRunningError=Pr�vodce instalac� zjistil, �e produkt %1 je nyn� spu�t�n.%n%nZav�ete pros�m v�echny instance tohoto produktu a pak pokra�ujte klepnut�m na tla��tko OK, nebo ukon�ete instalaci tla��tkem Zru�it.
UninstallAppRunningError=Pr�vodce odinstalac� zjistil, �e produkt %1 je nyn� spu�t�n.%n%nZav�ete pros�m v�echny instance tohoto produktu a pak pokra�ujte klepnut�m na tla��tko OK, nebo ukon�ete odinstalaci tla��tkem Zru�it.

; *** Startup questions
PrivilegesRequiredOverrideTitle=V�b�r re�imu pr�vodce instalac�
PrivilegesRequiredOverrideInstruction=Zvolte re�im instalace
PrivilegesRequiredOverrideText1=Produkt %1 lze nainstalovat pro v�echny u�ivatele (mus�te b�t p�ihl�eni s opr�vn�n�mi spr�vce), nebo pouze pro V�s.
PrivilegesRequiredOverrideText2=Produkt %1 lze nainstalovat pouze pro V�s, nebo pro v�echny u�ivatele (mus�te b�t p�ihl�eni s opr�vn�n�mi spr�vce).
PrivilegesRequiredOverrideAllUsers=Nainstalovat pro &v�echny u�ivatele
PrivilegesRequiredOverrideAllUsersRecommended=Nainstalovat pro &v�echny u�ivatele (doporu�uje se)
PrivilegesRequiredOverrideCurrentUser=Nainstalovat pouze pro &m�
PrivilegesRequiredOverrideCurrentUserRecommended=Nainstalovat pouze pro &m� (doporu�uje se)

; *** Misc. errors
ErrorCreatingDir=Pr�vodci instalac� se nepoda�ilo vytvo�it slo�ku "%1"
ErrorTooManyFilesInDir=Nelze vytvo�it soubor ve slo�ce "%1", proto�e tato slo�ka ji� obsahuje p��li� mnoho soubor�

; *** Setup common messages
ExitSetupTitle=Ukon�it pr�vodce instalac�
ExitSetupMessage=Instalace nebyla zcela dokon�ena. Jestli�e nyn� pr�vodce instalac� ukon��te, produkt nebude nainstalov�n.%n%nPr�vodce instalac� m��ete znovu spustit kdykoliv jindy a instalaci dokon�it.%n%nChcete pr�vodce instalac� ukon�it?
AboutSetupMenuItem=&O pr�vodci instalac�...
AboutSetupTitle=O pr�vodci instalac�
AboutSetupMessage=%1 verze %2%n%3%n%n%1 domovsk� str�nka:%n%4
AboutSetupNote=
TranslatorNote=Czech translation maintained by Ivo Bauer (bauer@ozm.cz), Lubos Stanek (lubek@users.sourceforge.net), Vitezslav Svejdar (vitezslav.svejdar@cuni.cz) and Jiri Fenz (jirifenz@gmail.com)

; *** Buttons
ButtonBack=< &Zp�t
ButtonNext=&Dal�� >
ButtonInstall=&Instalovat
ButtonOK=OK
ButtonCancel=Zru�it
ButtonYes=&Ano
ButtonYesToAll=Ano &v�em
ButtonNo=&Ne
ButtonNoToAll=N&e v�em
ButtonFinish=&Dokon�it
ButtonBrowse=&Proch�zet...
ButtonWizardBrowse=&Proch�zet...
ButtonNewFolder=&Vytvo�it novou slo�ku

; *** "Select Language" dialog messages
SelectLanguageTitle=V�b�r jazyka pr�vodce instalac�
SelectLanguageLabel=Zvolte jazyk, kter� se m� pou��t b�hem instalace.

; *** Common wizard text
ClickNext=Pokra�ujte klepnut�m na tla��tko Dal��, nebo ukon�ete pr�vodce instalac� tla��tkem Zru�it.
BeveledLabel=
BrowseDialogTitle=Zvolte slo�ku
BrowseDialogLabel=Z n�e uveden�ho seznamu vyberte slo�ku a klepn�te na tla��tko OK.
NewFolderName=Nov� slo�ka

; *** "Welcome" wizard page
WelcomeLabel1=V�t� V�s pr�vodce instalac� produktu [name].
WelcomeLabel2=Produkt [name/ver] bude nainstalov�n na V� po��ta�.%n%nD��ve ne� budete pokra�ovat, doporu�uje se zav��t ve�ker� spu�t�n� aplikace.

; *** "License Agreement" wizard page
WizardLicense=Licen�n� smlouva
LicenseLabel=D��ve ne� budete pokra�ovat, p�e�t�te si pros�m pozorn� n�sleduj�c� d�le�it� informace.
LicenseLabel3=P�e�t�te si pros�m n�sleduj�c� licen�n� smlouvu. Aby instalace mohla pokra�ovat, mus�te souhlasit s podm�nkami t�to smlouvy.
LicenseAccepted=&Souhlas�m s podm�nkami licen�n� smlouvy
LicenseNotAccepted=&Nesouhlas�m s podm�nkami licen�n� smlouvy

; *** "Information" wizard pages
WizardInfoBefore=Informace
InfoBeforeLabel=D��ve ne� budete pokra�ovat, p�e�t�te si pros�m pozorn� n�sleduj�c� d�le�it� informace.
InfoBeforeClickLabel=Pokra�ujte v instalaci klepnut�m na tla��tko Dal��.
WizardInfoAfter=Informace
InfoAfterLabel=D��ve ne� budete pokra�ovat, p�e�t�te si pros�m pozorn� n�sleduj�c� d�le�it� informace.
InfoAfterClickLabel=Pokra�ujte v instalaci klepnut�m na tla��tko Dal��.

; *** "User Information" wizard page
WizardUserInfo=Informace o u�ivateli
UserInfoDesc=Zadejte pros�m po�adovan� �daje.
UserInfoName=&U�ivatelsk� jm�no:
UserInfoOrg=&Spole�nost:
UserInfoSerial=S�&riov� ��slo:
UserInfoNameRequired=Mus�te zadat u�ivatelsk� jm�no.

; *** "Select Destination Location" wizard page
WizardSelectDir=Zvolte c�lov� um�st�n�
SelectDirDesc=Kam m� b�t produkt [name] nainstalov�n?
SelectDirLabel3=Pr�vodce nainstaluje produkt [name] do n�sleduj�c� slo�ky.
SelectDirBrowseLabel=Pokra�ujte klepnut�m na tla��tko Dal��. Chcete-li zvolit jinou slo�ku, klepn�te na tla��tko Proch�zet.
DiskSpaceGBLabel=Instalace vy�aduje nejm�n� [gb] GB voln�ho m�sta na disku.
DiskSpaceMBLabel=Instalace vy�aduje nejm�n� [mb] MB voln�ho m�sta na disku.
CannotInstallToNetworkDrive=Pr�vodce instalac� nem��e instalovat do s�ov� jednotky.
CannotInstallToUNCPath=Pr�vodce instalac� nem��e instalovat do cesty UNC.
InvalidPath=Mus�te zadat �plnou cestu v�etn� p�smene jednotky; nap��klad:%n%nC:\Aplikace%n%nnebo cestu UNC ve tvaru:%n%n\\server\sd�len� slo�ka
InvalidDrive=V�mi zvolen� jednotka nebo cesta UNC neexistuje nebo nen� dostupn�. Zvolte pros�m jin� um�st�n�.
DiskSpaceWarningTitle=Nedostatek m�sta na disku
DiskSpaceWarning=Pr�vodce instalac� vy�aduje nejm�n� %1 KB voln�ho m�sta pro instalaci produktu, ale na zvolen� jednotce je dostupn�ch pouze %2 KB.%n%nChcete p�esto pokra�ovat?
DirNameTooLong=N�zev slo�ky nebo cesta jsou p��li� dlouh�.
InvalidDirName=N�zev slo�ky nen� platn�.
BadDirName32=N�zev slo�ky nem��e obsahovat ��dn� z n�sleduj�c�ch znak�:%n%n%1
DirExistsTitle=Slo�ka existuje
DirExists=Slo�ka:%n%n%1%n%nji� existuje. M� se p�esto instalovat do t�to slo�ky?
DirDoesntExistTitle=Slo�ka neexistuje
DirDoesntExist=Slo�ka:%n%n%1%n%nneexistuje. M� b�t tato slo�ka vytvo�ena?

; *** "Select Components" wizard page
WizardSelectComponents=Zvolte sou��sti
SelectComponentsDesc=Jak� sou��sti maj� b�t nainstalov�ny?
SelectComponentsLabel2=Za�krtn�te sou��sti, kter� maj� b�t nainstalov�ny; sou��sti, kter� se nemaj� instalovat, ponechte neza�krtnut�. Pokra�ujte klepnut�m na tla��tko Dal��.
FullInstallation=�pln� instalace
; if possible don't translate 'Compact' as 'Minimal' (I mean 'Minimal' in your language)
CompactInstallation=Kompaktn� instalace
CustomInstallation=Voliteln� instalace
NoUninstallWarningTitle=Sou��sti existuj�
NoUninstallWarning=Pr�vodce instalac� zjistil, �e n�sleduj�c� sou��sti jsou ji� na Va�em po��ta�i nainstalov�ny:%n%n%1%n%nNezahrnete-li tyto sou��sti do v�b�ru, nebudou nyn� odinstalov�ny.%n%nChcete p�esto pokra�ovat?
ComponentSize1=%1 KB
ComponentSize2=%1 MB
ComponentsDiskSpaceGBLabel=Vybran� sou��sti vy�aduj� nejm�n� [gb] GB m�sta na disku.
ComponentsDiskSpaceMBLabel=Vybran� sou��sti vy�aduj� nejm�n� [mb] MB m�sta na disku.

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=Zvolte dal�� �lohy
SelectTasksDesc=Kter� dal�� �lohy maj� b�t provedeny?
SelectTasksLabel2=Zvolte dal�� �lohy, kter� maj� b�t provedeny v pr�b�hu instalace produktu [name], a pak pokra�ujte klepnut�m na tla��tko Dal��.

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=Vyberte slo�ku v nab�dce Start
SelectStartMenuFolderDesc=Kam m� pr�vodce instalac� um�stit z�stupce aplikace?
SelectStartMenuFolderLabel3=Pr�vodce instalac� vytvo�� z�stupce aplikace v n�sleduj�c� slo�ce nab�dky Start.
SelectStartMenuFolderBrowseLabel=Pokra�ujte klepnut�m na tla��tko Dal��. Chcete-li zvolit jinou slo�ku, klepn�te na tla��tko Proch�zet.
MustEnterGroupName=Mus�te zadat n�zev slo�ky.
GroupNameTooLong=N�zev slo�ky nebo cesta jsou p��li� dlouh�.
InvalidGroupName=N�zev slo�ky nen� platn�.
BadGroupName=N�zev slo�ky nem��e obsahovat ��dn� z n�sleduj�c�ch znak�:%n%n%1
NoProgramGroupCheck2=&Nevytv��et slo�ku v nab�dce Start

; *** "Ready to Install" wizard page
WizardReady=Instalace je p�ipravena
ReadyLabel1=Pr�vodce instalac� je nyn� p�ipraven nainstalovat produkt [name] na V� po��ta�.
ReadyLabel2a=Pokra�ujte v instalaci klepnut�m na tla��tko Instalovat. P�ejete-li si zm�nit n�kter� nastaven� instalace, klepn�te na tla��tko Zp�t.
ReadyLabel2b=Pokra�ujte v instalaci klepnut�m na tla��tko Instalovat.
ReadyMemoUserInfo=Informace o u�ivateli:
ReadyMemoDir=C�lov� um�st�n�:
ReadyMemoType=Typ instalace:
ReadyMemoComponents=Vybran� sou��sti:
ReadyMemoGroup=Slo�ka v nab�dce Start:
ReadyMemoTasks=Dal�� �lohy:

; *** TDownloadWizardPage wizard page and DownloadTemporaryFile
DownloadingLabel=Stahuj� se dal�� soubory...
ButtonStopDownload=&Zastavit stahov�n�
StopDownload=Ur�it� chcete stahov�n� zastavit?
ErrorDownloadAborted=Stahov�n� p�eru�eno
ErrorDownloadFailed=Stahov�n� selhalo: %1 %2
ErrorDownloadSizeFailed=Nepoda�ilo se zjistit velikost: %1 %2
ErrorFileHash1=Nepoda�ilo se ur�it kontroln� sou�et souboru: %1
ErrorFileHash2=Neplatn� kontroln� sou�et souboru: o�ek�v�no %1, nalezeno %2
ErrorProgress=Neplatn� pr�b�h: %1 of %2
ErrorFileSize=Neplatn� velikost souboru: o�ek�v�no %1, nalezeno %2

; *** TExtractionWizardPage wizard page and Extract7ZipArchive
ExtractionLabel=Extrahuj� se dal�� soubory...
ButtonStopExtraction=&Zastavit extrahov�n�
StopExtraction=Ur�it� chcete extrahov�n� zastavit?
ErrorExtractionAborted=Extrahov�n� p�eru�eno
ErrorExtractionFailed=Extrahov�n� selhalo: %1

; *** "Preparing to Install" wizard page
WizardPreparing=P��prava k instalaci
PreparingDesc=Pr�vodce instalac� p�ipravuje instalaci produktu [name] na V� po��ta�.
PreviousInstallNotCompleted=Instalace/odinstalace p�edchoz�ho produktu nebyla zcela dokon�ena. Aby mohla b�t dokon�ena, mus�te restartovat V� po��ta�.%n%nPo restartov�n� Va�eho po��ta�e spus�te znovu pr�vodce instalac�, aby bylo mo�n� dokon�it instalaci produktu [name].
CannotContinue=Pr�vodce instalac� nem��e pokra�ovat. Ukon�ete pros�m pr�vodce instalac� klepnut�m na tla��tko Zru�it.
ApplicationsFound=N�sleduj�c� aplikace p�istupuj� k soubor�m, kter� je t�eba b�hem instalace aktualizovat. Doporu�uje se povolit pr�vodci instalac�, aby tyto aplikace automaticky zav�el.
ApplicationsFound2=N�sleduj�c� aplikace p�istupuj� k soubor�m, kter� je t�eba b�hem instalace aktualizovat. Doporu�uje se povolit pr�vodci instalac�, aby tyto aplikace automaticky zav�el. Po dokon�en� instalace se pr�vodce instalac� pokus� aplikace restartovat.
CloseApplications=&Zav��t aplikace automaticky
DontCloseApplications=&Nezav�rat aplikace
ErrorCloseApplications=Pr�vodci instalac� se nepoda�ilo automaticky zav��t v�echny aplikace. D��ve ne� budete pokra�ovat, doporu�uje se zav��t ve�ker� aplikace p�istupuj�c� k soubor�m, kter� je t�eba b�hem instalace aktualizovat.
PrepareToInstallNeedsRestart=Pr�vodce instalac� mus� restartovat V� po��ta�. Po restartov�n� Va�eho po��ta�e spus�te pr�vodce instalac� znovu, aby bylo mo�n� dokon�it instalaci produktu [name].%n%nChcete jej restartovat nyn�?

; *** "Installing" wizard page
WizardInstalling=Instalov�n�
InstallingLabel=�ekejte pros�m, dokud pr�vodce instalac� nedokon�� instalaci produktu [name] na V� po��ta�.

; *** "Setup Completed" wizard page
FinishedHeadingLabel=Dokon�uje se instalace produktu [name]
FinishedLabelNoIcons=Pr�vodce instalac� dokon�il instalaci produktu [name] na V� po��ta�.
FinishedLabel=Pr�vodce instalac� dokon�il instalaci produktu [name] na V� po��ta�. Produkt lze spustit pomoc� nainstalovan�ch z�stupc�.
ClickFinish=Ukon�ete pr�vodce instalac� klepnut�m na tla��tko Dokon�it.
FinishedRestartLabel=K dokon�en� instalace produktu [name] je nezbytn�, aby pr�vodce instalac� restartoval V� po��ta�. Chcete jej restartovat nyn�?
FinishedRestartMessage=K dokon�en� instalace produktu [name] je nezbytn�, aby pr�vodce instalac� restartoval V� po��ta�.%n%nChcete jej restartovat nyn�?
ShowReadmeCheck=Ano, chci zobrazit dokument "�TIMNE"
YesRadio=&Ano, chci nyn� restartovat po��ta�
NoRadio=&Ne, po��ta� restartuji pozd�ji
; used for example as 'Run MyProg.exe'
RunEntryExec=Spustit %1
; used for example as 'View Readme.txt'
RunEntryShellExec=Zobrazit %1

; *** "Setup Needs the Next Disk" stuff
ChangeDiskTitle=Pr�vodce instalac� vy�aduje dal�� disk
SelectDiskLabel2=Vlo�te pros�m disk %1 a klepn�te na tla��tko OK.%n%nPokud se soubory na tomto disku nach�zej� v jin� slo�ce ne� v t�, kter� je zobrazena n�e, pak zadejte spr�vnou cestu nebo ji zvolte klepnut�m na tla��tko Proch�zet.
PathLabel=&Cesta:
FileNotInDir2=Soubor "%1" nelze naj�t v "%2". Vlo�te pros�m spr�vn� disk nebo zvolte jinou slo�ku.
SelectDirectoryLabel=Specifikujte pros�m um�st�n� dal��ho disku.

; *** Installation phase messages
SetupAborted=Instalace nebyla zcela dokon�ena.%n%nOpravte pros�m chybu a spus�te pr�vodce instalac� znovu.
AbortRetryIgnoreSelectAction=Zvolte akci
AbortRetryIgnoreRetry=&Zopakovat akci
AbortRetryIgnoreIgnore=&Ignorovat chybu a pokra�ovat
AbortRetryIgnoreCancel=Zru�it instalaci

; *** Installation status messages
StatusClosingApplications=Zav�raj� se aplikace...
StatusCreateDirs=Vytv��ej� se slo�ky...
StatusExtractFiles=Extrahuj� se soubory...
StatusCreateIcons=Vytv��ej� se z�stupci...
StatusCreateIniEntries=Vytv��ej� se z�znamy v inicializa�n�ch souborech...
StatusCreateRegistryEntries=Vytv��ej� se z�znamy v syst�mov�m registru...
StatusRegisterFiles=Registruj� se soubory...
StatusSavingUninstall=Ukl�daj� se informace pro odinstalaci produktu...
StatusRunProgram=Dokon�uje se instalace...
StatusRestartingApplications=Restartuj� se aplikace...
StatusRollback=Proveden� zm�ny se vracej� zp�t...

; *** Misc. errors
ErrorInternal2=Intern� chyba: %1
ErrorFunctionFailedNoCode=Funkce %1 selhala
ErrorFunctionFailed=Funkce %1 selhala; k�d %2
ErrorFunctionFailedWithMessage=Funkce %1 selhala; k�d %2.%n%3
ErrorExecutingProgram=Nelze spustit soubor:%n%1

; *** Registry errors
ErrorRegOpenKey=Do�lo k chyb� p�i otev�r�n� kl��e syst�mov�ho registru:%n%1\%2
ErrorRegCreateKey=Do�lo k chyb� p�i vytv��en� kl��e syst�mov�ho registru:%n%1\%2
ErrorRegWriteKey=Do�lo k chyb� p�i z�pisu do kl��e syst�mov�ho registru:%n%1\%2

; *** INI errors
ErrorIniEntry=Do�lo k chyb� p�i vytv��en� z�znamu v inicializa�n�m souboru "%1".

; *** File copying errors
FileAbortRetryIgnoreSkipNotRecommended=&P�esko�it tento soubor (nedoporu�uje se)
FileAbortRetryIgnoreIgnoreNotRecommended=&Ignorovat chybu a pokra�ovat (nedoporu�uje se)
SourceIsCorrupted=Zdrojov� soubor je po�kozen
SourceDoesntExist=Zdrojov� soubor "%1" neexistuje
ExistingFileReadOnly2=Nelze nahradit existuj�c� soubor, proto�e je ur�en pouze pro �ten�.
ExistingFileReadOnlyRetry=&Odstranit atribut "pouze pro �ten�" a zopakovat akci
ExistingFileReadOnlyKeepExisting=&Ponechat existuj�c� soubor
ErrorReadingExistingDest=Do�lo k chyb� p�i pokusu o �ten� existuj�c�ho souboru:
FileExistsSelectAction=Zvolte akci
FileExists2=Soubor ji� existuje.
FileExistsOverwriteExisting=&Nahradit existuj�c� soubor
FileExistsKeepExisting=&Ponechat existuj�c� soubor
FileExistsOverwriteOrKeepAll=&Zachovat se stejn� u dal��ch konflikt�
ExistingFileNewerSelectAction=Zvolte akci
ExistingFileNewer2=Existuj�c� soubor je nov�j�� ne� ten, kter� se pr�vodce instalac� pokou�� instalovat.
ExistingFileNewerOverwriteExisting=&Nahradit existuj�c� soubor
ExistingFileNewerKeepExisting=&Ponechat existuj�c� soubor (doporu�uje se)
ExistingFileNewerOverwriteOrKeepAll=&Zachovat se stejn� u dal��ch konflikt�
ErrorChangingAttr=Do�lo k chyb� p�i pokusu o zm�nu atribut� existuj�c�ho souboru:
ErrorCreatingTemp=Do�lo k chyb� p�i pokusu o vytvo�en� souboru v c�lov� slo�ce:
ErrorReadingSource=Do�lo k chyb� p�i pokusu o �ten� zdrojov�ho souboru:
ErrorCopying=Do�lo k chyb� p�i pokusu o zkop�rov�n� souboru:
ErrorReplacingExistingFile=Do�lo k chyb� p�i pokusu o nahrazen� existuj�c�ho souboru:
ErrorRestartReplace=Funkce "RestartReplace" pr�vodce instalac� selhala:
ErrorRenamingTemp=Do�lo k chyb� p�i pokusu o p�ejmenov�n� souboru v c�lov� slo�ce:
ErrorRegisterServer=Nelze zaregistrovat DLL/OCX: %1
ErrorRegSvr32Failed=Vol�n� RegSvr32 selhalo s n�vratov�m k�dem %1
ErrorRegisterTypeLib=Nelze zaregistrovat typovou knihovnu: %1

; *** Uninstall display name markings
; used for example as 'My Program (32-bit)'
UninstallDisplayNameMark=%1 (%2)
; used for example as 'My Program (32-bit, All users)'
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32bitov�
UninstallDisplayNameMark64Bit=64bitov�
UninstallDisplayNameMarkAllUsers=V�ichni u�ivatel�
UninstallDisplayNameMarkCurrentUser=Aktu�ln� u�ivatel

; *** Post-installation errors
ErrorOpeningReadme=Do�lo k chyb� p�i pokusu o otev�en� dokumentu "�TIMNE".
ErrorRestartingComputer=Pr�vodci instalac� se nepoda�ilo restartovat V� po��ta�. Restartujte jej pros�m ru�n�.

; *** Uninstaller messages
UninstallNotFound=Soubor "%1" neexistuje. Produkt nelze odinstalovat.
UninstallOpenError=Soubor "%1" nelze otev��t. Produkt nelze odinstalovat.
UninstallUnsupportedVer=Form�t souboru se z�znamy k odinstalaci produktu "%1" nebyl touto verz� pr�vodce odinstalac� rozpozn�n. Produkt nelze odinstalovat
UninstallUnknownEntry=V souboru obsahuj�c�m informace k odinstalaci produktu byla zji�t�na nezn�m� polo�ka (%1)
ConfirmUninstall=Ur�it� chcete produkt %1 a v�echny jeho sou��sti odinstalovat?
UninstallOnlyOnWin64=Tento produkt lze odinstalovat pouze v 64-bitov�ch verz�ch MS Windows.
OnlyAdminCanUninstall=K odinstalaci tohoto produktu mus�te b�t p�ihl�eni s opr�vn�n�mi spr�vce.
UninstallStatusLabel=�ekejte pros�m, dokud produkt %1 nebude odinstalov�n z Va�eho po��ta�e.
UninstalledAll=Produkt %1 byl z Va�eho po��ta�e �sp�n� odinstalov�n.
UninstalledMost=Produkt %1 byl odinstalov�n.%n%nN�kter� jeho sou��sti se odinstalovat nepoda�ilo. M��ete je v�ak odstranit ru�n�.
UninstalledAndNeedsRestart=K dokon�en� odinstalace produktu %1 je nezbytn�, aby pr�vodce odinstalac� restartoval V� po��ta�.%n%nChcete jej restartovat nyn�?
UninstallDataCorrupted=Soubor "%1" je po�kozen. Produkt nelze odinstalovat

; *** Uninstallation phase messages
ConfirmDeleteSharedFileTitle=Odebrat sd�len� soubor?
ConfirmDeleteSharedFile2=Syst�m indikuje, �e n�sleduj�c� sd�len� soubor nen� pou��v�n ��dn�mi jin�mi aplikacemi. M� b�t tento sd�len� soubor pr�vodcem odinstalac� odstran�n?%n%nPokud n�kter� aplikace tento soubor pou��vaj�, pak po jeho odstran�n� nemusej� pracovat spr�vn�. Pokud si nejste jisti, zvolte Ne. Ponech�n� tohoto souboru ve Va�em syst�mu nezp�sob� ��dnou �kodu.
SharedFileNameLabel=N�zev souboru:
SharedFileLocationLabel=Um�st�n�:
WizardUninstalling=Stav odinstalace
StatusUninstalling=Prob�h� odinstalace produktu %1...

; *** Shutdown block reasons
ShutdownBlockReasonInstallingApp=Prob�h� instalace produktu %1.
ShutdownBlockReasonUninstallingApp=Prob�h� odinstalace produktu %1.

; The custom messages below aren't used by Setup itself, but if you make
; use of them in your scripts, you'll want to translate them.

[CustomMessages]

NameAndVersion=%1 verze %2
AdditionalIcons=Dal�� z�stupci:
CreateDesktopIcon=Vytvo�it z�stupce na &plo�e
CreateQuickLaunchIcon=Vytvo�it z�stupce na panelu &Snadn� spu�t�n�
ProgramOnTheWeb=Aplikace %1 na internetu
UninstallProgram=Odinstalovat aplikaci %1
LaunchProgram=Spustit aplikaci %1
AssocFileExtension=Vytvo�it &asociaci mezi soubory typu %2 a aplikac� %1
AssocingFileExtension=Vytv��� se asociace mezi soubory typu %2 a aplikac� %1...
AutoStartProgramGroupDescription=Po spu�t�n�:
AutoStartProgram=Spou�t�t aplikaci %1 automaticky
AddonHostProgramNotFound=Aplikace %1 nebyla ve V�mi zvolen� slo�ce nalezena.%n%nChcete p�esto pokra�ovat?
