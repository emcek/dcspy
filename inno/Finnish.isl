; *** Inno Setup version 6.4.0+ Finnish messages ***
;
; Finnish translation by Antti Karttunen
; E-mail: antti.j.karttunen@iki.fi
; Last modification date: 2024-11-30

[LangOptions]
LanguageName=Suomi
LanguageID=$040B
LanguageCodePage=1252

[Messages]

; *** Application titles
SetupAppTitle=Asennus
SetupWindowTitle=%1 - Asennus
UninstallAppTitle=Asennuksen poisto
UninstallAppFullTitle=%1 - Asennuksen poisto

; *** Misc. common
InformationTitle=Ilmoitus
ConfirmTitle=Varmistus
ErrorTitle=Virhe

; *** SetupLdr messages
SetupLdrStartupMessage=T�ll� asennusohjelmalla asennetaan %1. Haluatko jatkaa?
LdrCannotCreateTemp=V�liaikaistiedostoa ei voitu luoda. Asennus keskeytettiin
LdrCannotExecTemp=V�liaikaisessa hakemistossa olevaa tiedostoa ei voitu suorittaa. Asennus keskeytettiin

; *** Startup error messages
LastErrorMessage=%1.%n%nVirhe %2: %3
SetupFileMissing=Tiedostoa %1 ei l�ydy asennushakemistosta. Korjaa ongelma tai hanki uusi kopio ohjelmasta.
SetupFileCorrupt=Asennustiedostot ovat vaurioituneet. Hanki uusi kopio ohjelmasta.
SetupFileCorruptOrWrongVer=Asennustiedostot ovat vaurioituneet tai ovat ep�yhteensopivia t�m�n Asennuksen version kanssa. Korjaa ongelma tai hanki uusi kopio ohjelmasta.
InvalidParameter=Virheellinen komentoriviparametri:%n%n%1
SetupAlreadyRunning=Asennus on jo k�ynniss�.
WindowsVersionNotSupported=T�m� ohjelma ei tue k�yt�ss� olevaa Windowsin versiota.
WindowsServicePackRequired=T�m� ohjelma vaatii %1 Service Pack %2 -p�ivityksen tai my�hemm�n.
NotOnThisPlatform=T�m� ohjelma ei toimi %1-k�ytt�j�rjestelm�ss�.
OnlyOnThisPlatform=T�m� ohjelma toimii vain %1-k�ytt�j�rjestelm�ss�.
OnlyOnTheseArchitectures=T�m� ohjelma voidaan asentaa vain niihin Windowsin versioihin, jotka on suunniteltu seuraaville prosessorityypeille:%n%n%1
WinVersionTooLowError=T�m� ohjelma vaatii version %2 tai my�hemm�n %1-k�ytt�j�rjestelm�st�.
WinVersionTooHighError=T�t� ohjelmaa ei voi asentaa %1-k�ytt�j�rjestelm�n versioon %2 tai my�hemp��n.
AdminPrivilegesRequired=Sinun t�ytyy kirjautua sis��n j�rjestelm�nvalvojana asentaaksesi t�m�n ohjelman.
PowerUserPrivilegesRequired=Sinun t�ytyy kirjautua sis��n j�rjestelm�nvalvojana tai tehok�ytt�j�n� asentaaksesi t�m�n ohjelman.
SetupAppRunningError=Asennus l�ysi k�ynniss� olevan kopion ohjelmasta %1.%n%nSulje kaikki k�ynniss� olevat kopiot ohjelmasta ja valitse OK jatkaaksesi, tai valitse Peruuta poistuaksesi.
UninstallAppRunningError=Asennuksen poisto l�ysi k�ynniss� olevan kopion ohjelmasta %1.%n%nSulje kaikki k�ynniss� olevat kopiot ohjelmasta ja valitse OK jatkaaksesi, tai valitse Peruuta poistuaksesi.

; *** Startup questions
PrivilegesRequiredOverrideTitle=Valitse asennustapa
PrivilegesRequiredOverrideInstruction=Valitse, kenen k�ytt��n ohjelma asennetaan
PrivilegesRequiredOverrideText1=%1 voidaan asentaa kaikille k�ytt�jille (vaatii j�rjestelm�nvalvojan oikeudet) tai vain sinun k�ytt��si.
PrivilegesRequiredOverrideText2=%1 voidaan asentaa vain sinun k�ytt��si tai kaikille k�ytt�jille (vaatii j�rjestelm�nvalvojan oikeudet).
PrivilegesRequiredOverrideAllUsers=Asenna &kaikille k�ytt�jille
PrivilegesRequiredOverrideAllUsersRecommended=Asenna &kaikille k�ytt�jille (suositus)
PrivilegesRequiredOverrideCurrentUser=Asenna vain &minun k�ytt��ni
PrivilegesRequiredOverrideCurrentUserRecommended=Asenna vain &minun k�ytt��ni (suositus)

; *** Misc. errors
ErrorCreatingDir=Asennus ei voinut luoda hakemistoa "%1"
ErrorTooManyFilesInDir=Tiedoston luominen hakemistoon "%1" ep�onnistui, koska se sis�lt�� liian monta tiedostoa

; *** Setup common messages
ExitSetupTitle=Poistu Asennuksesta
ExitSetupMessage=Asennus ei ole valmis. Jos lopetat nyt, ohjelmaa ei asenneta.%n%nVoit ajaa Asennuksen toiste asentaaksesi ohjelman.%n%nLopetetaanko Asennus?
AboutSetupMenuItem=&Tietoja Asennuksesta...
AboutSetupTitle=Tietoja Asennuksesta
AboutSetupMessage=%1 versio %2%n%3%n%n%1 -ohjelman kotisivu:%n%4
AboutSetupNote=
TranslatorNote=Suomenkielinen k��nn�s: Antti Karttunen (antti.j.karttunen@iki.fi)

; *** Buttons
ButtonBack=< &Takaisin
ButtonNext=&Seuraava >
ButtonInstall=&Asenna
ButtonOK=OK
ButtonCancel=Peruuta
ButtonYes=&Kyll�
ButtonYesToAll=Kyll� k&aikkiin
ButtonNo=&Ei
ButtonNoToAll=E&i kaikkiin
ButtonFinish=&Lopeta
ButtonBrowse=S&elaa...
ButtonWizardBrowse=S&elaa...
ButtonNewFolder=&Luo uusi kansio

; *** "Select Language" dialog messages
SelectLanguageTitle=Valitse Asennuksen kieli
SelectLanguageLabel=Valitse asentamisen aikana k�ytett�v� kieli.

; *** Common wizard text
ClickNext=Valitse Seuraava jatkaaksesi tai Peruuta poistuaksesi.
BeveledLabel=
BrowseDialogTitle=Selaa kansioita
BrowseDialogLabel=Valitse kansio allaolevasta listasta ja valitse sitten OK jatkaaksesi.
NewFolderName=Uusi kansio

; *** "Welcome" wizard page
WelcomeLabel1=Tervetuloa [name] -asennusohjelmaan.
WelcomeLabel2=T�ll� asennusohjelmalla koneellesi asennetaan [name/ver]. %n%nOn suositeltavaa, ett� suljet kaikki muut k�ynniss� olevat sovellukset ennen jatkamista. T�m� auttaa v�ltt�m��n ristiriitatilanteita asennuksen aikana.

; *** "License Agreement" wizard page
WizardLicense=K�ytt�oikeussopimus
LicenseLabel=Lue seuraava t�rke� tiedotus ennen kuin jatkat.
LicenseLabel3=Lue seuraava k�ytt�oikeussopimus tarkasti. Sinun t�ytyy hyv�ksy� sopimus, jos haluat jatkaa asentamista.
LicenseAccepted=&Hyv�ksyn sopimuksen
LicenseNotAccepted=&En hyv�ksy sopimusta

; *** "Information" wizard pages
WizardInfoBefore=Tiedotus
InfoBeforeLabel=Lue seuraava t�rke� tiedotus ennen kuin jatkat.
InfoBeforeClickLabel=Kun olet valmis jatkamaan asentamista, valitse Seuraava.
WizardInfoAfter=Tiedotus
InfoAfterLabel=Lue seuraava t�rke� tiedotus ennen kuin jatkat.
InfoAfterClickLabel=Kun olet valmis jatkamaan asentamista, valitse Seuraava.

; *** "Select Destination Directory" wizard page
WizardUserInfo=K�ytt�j�tiedot
UserInfoDesc=Anna pyydetyt tiedot.
UserInfoName=K�ytt�j�n &nimi:
UserInfoOrg=&Yritys:
UserInfoSerial=&Tunnuskoodi:
UserInfoNameRequired=Sinun t�ytyy antaa nimi.

; *** "Select Destination Location" wizard page
WizardSelectDir=Valitse kohdekansio
SelectDirDesc=Mihin [name] asennetaan?
SelectDirLabel3=[name] asennetaan t�h�n kansioon.
SelectDirBrowseLabel=Valitse Seuraava jatkaaksesi. Jos haluat vaihtaa kansiota, valitse Selaa.
DiskSpaceGBLabel=Vapaata levytilaa tarvitaan v�hint��n [gb] Gt.
DiskSpaceMBLabel=Vapaata levytilaa tarvitaan v�hint��n [mb] Mt.
CannotInstallToNetworkDrive=Asennus ei voi asentaa ohjelmaa verkkoasemalle.
CannotInstallToUNCPath=Asennus ei voi asentaa ohjelmaa UNC-polun alle.
InvalidPath=Anna t�ydellinen polku levyaseman kirjaimen kanssa. Esimerkiksi %nC:\OHJELMA%n%ntai UNC-polku muodossa %n%n\\palvelin\resurssi
InvalidDrive=Valitsemaasi asemaa tai UNC-polkua ei ole olemassa tai sit� ei voi k�ytt��. Valitse toinen asema tai UNC-polku.
DiskSpaceWarningTitle=Ei tarpeeksi vapaata levytilaa
DiskSpaceWarning=Asennus vaatii v�hint��n %1 kt vapaata levytilaa, mutta valitulla levyasemalla on vain %2 kt vapaata levytilaa.%n%nHaluatko jatkaa t�st� huolimatta?
DirNameTooLong=Kansion nimi tai polku on liian pitk�.
InvalidDirName=Virheellinen kansion nimi.
BadDirName32=Kansion nimess� ei saa olla seuraavia merkkej�:%n%n%1
DirExistsTitle=Kansio on olemassa
DirExists=Kansio:%n%n%1%n%non jo olemassa. Haluatko kuitenkin suorittaa asennuksen t�h�n kansioon?
DirDoesntExistTitle=Kansiota ei ole olemassa
DirDoesntExist=Kansiota%n%n%1%n%nei ole olemassa. Luodaanko kansio?

; *** "Select Components" wizard page
WizardSelectComponents=Valitse asennettavat osat
SelectComponentsDesc=Mitk� osat asennetaan?
SelectComponentsLabel2=Valitse ne osat, jotka haluat asentaa, ja poista niiden osien valinta, joita et halua asentaa. Valitse Seuraava, kun olet valmis.
FullInstallation=Normaali asennus
CompactInstallation=Suppea asennus
CustomInstallation=Mukautettu asennus
NoUninstallWarningTitle=Asennettuja osia l�ydettiin
NoUninstallWarning=Seuraavat osat on jo asennettu koneelle:%n%n%1%n%nN�iden osien valinnan poistaminen ei poista niit� koneelta.%n%nHaluatko jatkaa t�st� huolimatta?
ComponentSize1=%1 kt
ComponentSize2=%1 Mt
ComponentsDiskSpaceGBLabel=Nykyiset valinnat vaativat v�hint��n [gb] Gt levytilaa.
ComponentsDiskSpaceMBLabel=Nykyiset valinnat vaativat v�hint��n [mb] Mt levytilaa.

; *** "Select Additional Tasks" wizard page
WizardSelectTasks=Valitse muut toiminnot
SelectTasksDesc=Mit� muita toimintoja suoritetaan?
SelectTasksLabel2=Valitse muut toiminnot, jotka haluat Asennuksen suorittavan samalla kun [name] asennetaan. Valitse Seuraava, kun olet valmis.

; *** "Select Start Menu Folder" wizard page
WizardSelectProgramGroup=Valitse K�ynnist�-valikon kansio
SelectStartMenuFolderDesc=Mihin ohjelman pikakuvakkeet sijoitetaan?
SelectStartMenuFolderLabel3=Ohjelman pikakuvakkeet luodaan t�h�n K�ynnist�-valikon kansioon.
SelectStartMenuFolderBrowseLabel=Valitse Seuraava jatkaaksesi. Jos haluat vaihtaa kansiota, valitse Selaa.
MustEnterGroupName=Kansiolle pit�� antaa nimi.
GroupNameTooLong=Kansion nimi tai polku on liian pitk�.
InvalidGroupName=Virheellinen kansion nimi.
BadGroupName=Kansion nimess� ei saa olla seuraavia merkkej�:%n%n%1
NoProgramGroupCheck2=�l� luo k&ansiota K�ynnist�-valikkoon

; *** "Ready to Install" wizard page
WizardReady=Valmiina asennukseen
ReadyLabel1=[name] on nyt valmis asennettavaksi.
ReadyLabel2a=Valitse Asenna jatkaaksesi asentamista tai valitse Takaisin, jos haluat tarkastella tekemi�si asetuksia tai muuttaa niit�.
ReadyLabel2b=Valitse Asenna jatkaaksesi asentamista.
ReadyMemoUserInfo=K�ytt�j�tiedot:
ReadyMemoDir=Kohdekansio:
ReadyMemoType=Asennustyyppi:
ReadyMemoComponents=Asennettavaksi valitut osat:
ReadyMemoGroup=K�ynnist�-valikon kansio:
ReadyMemoTasks=Muut toiminnot:

; *** TDownloadWizardPage wizard page and DownloadTemporaryFile
DownloadingLabel=Ladataan tarvittavia tiedostoja...
ButtonStopDownload=&Pys�yt� lataus
StopDownload=Oletko varma, ett� haluat pys�ytt�� tiedostojen latauksen?
ErrorDownloadAborted=Tiedostojen lataaminen keskeytettiin
ErrorDownloadFailed=Tiedoston lataaminen ep�onnistui: %1 %2
ErrorDownloadSizeFailed=Latauksen koon noutaminen ep�onnistui: %1 %2
ErrorFileHash1=Tiedoston tiivisteen luominen ep�onnistui: %1
ErrorFileHash2=Tiedoston tiiviste on virheellinen: odotettu %1, l�ydetty %2
ErrorProgress=Virheellinen edistyminen: %1 / %2
ErrorFileSize=Virheellinen tiedoston koko: odotettu %1, l�ydetty %2

; *** TExtractionWizardPage wizard page and Extract7ZipArchive
ExtractionLabel=Puretaan tarvittavia tiedostoja...
ButtonStopExtraction=&Pys�yt� purku
StopExtraction=Oletko varma, ett� haluat pys�ytt�� tiedostojen purkamisen?
ErrorExtractionAborted=Tiedostojen purkaminen keskeytettiin
ErrorExtractionFailed=Tiedoston purkaminen ep�onnistui: %1

; *** "Preparing to Install" wizard page
WizardPreparing=Valmistellaan asennusta
PreparingDesc=Valmistaudutaan asentamaan [name] koneellesi.
PreviousInstallNotCompleted=Edellisen ohjelman asennus tai asennuksen poisto ei ole valmis. Sinun t�ytyy k�ynnist�� kone uudelleen viimeistell�ksesi edellisen asennuksen.%n%nAja [name] -asennusohjelma uudestaan, kun olet k�ynnist�nyt koneen uudelleen.
CannotContinue=Asennusta ei voida jatkaa. Valitse Peruuta poistuaksesi.
ApplicationsFound=Seuraavat sovellukset k�ytt�v�t tiedostoja, joita Asennuksen pit�� p�ivitt��. On suositeltavaa, ett� annat Asennuksen sulkea n�m� sovellukset automaattisesti.
ApplicationsFound2=Seuraavat sovellukset k�ytt�v�t tiedostoja, joita Asennuksen pit�� p�ivitt��. On suositeltavaa, ett� annat Asennuksen sulkea n�m� sovellukset automaattisesti. Valmistumisen j�lkeen Asennus yritt�� uudelleenk�ynnist�� sovellukset.
CloseApplications=&Sulje sovellukset automaattisesti
DontCloseApplications=&�l� sulje sovelluksia
ErrorCloseApplications=Asennus ei pystynyt sulkemaan tarvittavia sovelluksia automaattisesti. On suositeltavaa, ett� ennen jatkamista suljet sovellukset, jotka k�ytt�v�t asennuksen aikana p�ivitett�vi� tiedostoja.
PrepareToInstallNeedsRestart=Asennuksen t�ytyy k�ynnist�� tietokone uudelleen. Aja Asennus uudelleenk�ynnistyksen j�lkeen, jotta [name] voidaan asentaa.%n%nHaluatko k�ynnist�� tietokoneen uudelleen nyt?

; *** "Installing" wizard page
WizardInstalling=Asennus k�ynniss�
InstallingLabel=Odota, kun [name] asennetaan koneellesi.

; *** "Setup Completed" wizard page
FinishedHeadingLabel=[name] - Asennuksen viimeistely
FinishedLabelNoIcons=[name] on nyt asennettu koneellesi.
FinishedLabel=[name] on nyt asennettu. Sovellus voidaan k�ynnist�� valitsemalla jokin asennetuista kuvakkeista.
ClickFinish=Valitse Lopeta poistuaksesi Asennuksesta.
FinishedRestartLabel=Jotta [name] saataisiin asennettua loppuun, pit�� kone k�ynnist�� uudelleen. Haluatko k�ynnist�� koneen uudelleen nyt?
FinishedRestartMessage=Jotta [name] saataisiin asennettua loppuun, pit�� kone k�ynnist�� uudelleen.%n%nHaluatko k�ynnist�� koneen uudelleen nyt?
ShowReadmeCheck=Kyll�, haluan n�hd� LUEMINUT-tiedoston
YesRadio=&Kyll�, k�ynnist� kone uudelleen
NoRadio=&Ei, k�ynnist�n koneen uudelleen my�hemmin
RunEntryExec=K�ynnist� %1
RunEntryShellExec=N�yt� %1

; *** "Setup Needs the Next Disk" stuff
ChangeDiskTitle=Asennus tarvitsee seuraavan levykkeen
SelectDiskLabel2=Aseta levyke %1 asemaan ja valitse OK. %n%nJos joku toinen kansio sis�lt�� levykkeen tiedostot, anna oikea polku tai valitse Selaa.
PathLabel=&Polku:
FileNotInDir2=Tiedostoa "%1" ei l�ytynyt l�hteest� "%2". Aseta oikea levyke asemaan tai valitse toinen kansio.
SelectDirectoryLabel=M��rit� seuraavan levykkeen sis�ll�n sijainti.

; *** Installation phase messages
SetupAborted=Asennusta ei suoritettu loppuun.%n%nKorjaa ongelma ja suorita Asennus uudelleen.
AbortRetryIgnoreSelectAction=Valitse toiminto
AbortRetryIgnoreRetry=&Yrit� uudelleen
AbortRetryIgnoreIgnore=&Jatka virheest� huolimatta
AbortRetryIgnoreCancel=Peruuta asennus

; *** Installation status messages
StatusClosingApplications=Suljetaan sovellukset...
StatusCreateDirs=Luodaan hakemistoja...
StatusExtractFiles=Puretaan tiedostoja...
StatusCreateIcons=Luodaan pikakuvakkeita...
StatusCreateIniEntries=Luodaan INI-merkint�j�...
StatusCreateRegistryEntries=Luodaan rekisterimerkint�j�...
StatusRegisterFiles=Rekister�id��n tiedostoja...
StatusSavingUninstall=Tallennetaan Asennuksen poiston tietoja...
StatusRunProgram=Viimeistell��n asennusta...
StatusRestartingApplications=Uudelleenk�ynnistet��n sovellukset...
StatusRollback=Peruutetaan tehdyt muutokset...

; *** Misc. errors
ErrorInternal2=Sis�inen virhe: %1
ErrorFunctionFailedNoCode=%1 ep�onnistui
ErrorFunctionFailed=%1 ep�onnistui; virhekoodi %2
ErrorFunctionFailedWithMessage=%1 ep�onnistui; virhekoodi %2.%n%3
ErrorExecutingProgram=Virhe suoritettaessa tiedostoa%n%1

; *** Shutdown block reasons
ShutdownBlockReasonInstallingApp=Asennetaan %1.
ShutdownBlockReasonUninstallingApp=Poistetaan %1.

; *** Registry errors
ErrorRegOpenKey=Virhe avattaessa rekisteriavainta%n%1\%2
ErrorRegCreateKey=Virhe luotaessa rekisteriavainta%n%1\%2
ErrorRegWriteKey=Virhe kirjoitettaessa rekisteriavaimeen%n%1\%2

; *** INI errors
ErrorIniEntry=Virhe luotaessa INI-merkint�� tiedostoon "%1".

; *** File copying errors
FileAbortRetryIgnoreSkipNotRecommended=&Ohita t�m� tiedosto (ei suositeltavaa)
FileAbortRetryIgnoreIgnoreNotRecommended=&Jatka virheest� huolimatta (ei suositeltavaa)
SourceIsCorrupted=L�hdetiedosto on vaurioitunut
SourceDoesntExist=L�hdetiedostoa "%1" ei ole olemassa
ExistingFileReadOnly2=Nykyist� tiedostoa ei voitu korvata, koska se on Vain luku -tiedosto.
ExistingFileReadOnlyRetry=&Poista Vain luku -asetus ja yrit� uudelleen
ExistingFileReadOnlyKeepExisting=&S�ilyt� nykyinen tiedosto
ErrorReadingExistingDest=Virhe luettaessa nykyist� tiedostoa:
FileExistsSelectAction=Valitse toiminto
FileExists2=Tiedosto on jo olemassa.
FileExistsOverwriteExisting=Korvaa &olemassa oleva tiedosto
FileExistsKeepExisting=&S�ilyt� olemassa oleva tiedosto
FileExistsOverwriteOrKeepAll=&Hoida muut vastaavat tilanteet samalla tavalla
ExistingFileNewerSelectAction=Valitse toiminto
ExistingFileNewer2=Olemassa oleva tiedosto on uudempi kuin Asennuksen sis�lt�m� tiedosto.
ExistingFileNewerOverwriteExisting=Korvaa &olemassa oleva tiedosto
ExistingFileNewerKeepExisting=&S�ilyt� olemassa oleva tiedosto (suositeltavaa)
ExistingFileNewerOverwriteOrKeepAll=&Hoida muut vastaavat tilanteet samalla tavalla
ErrorChangingAttr=Virhe vaihdettaessa nykyisen tiedoston m��ritteit�:
ErrorCreatingTemp=Virhe luotaessa tiedostoa kohdehakemistoon:
ErrorReadingSource=Virhe luettaessa l�hdetiedostoa:
ErrorCopying=Virhe kopioitaessa tiedostoa:
ErrorReplacingExistingFile=Virhe korvattaessa nykyist� tiedostoa:
ErrorRestartReplace=RestartReplace-komento ep�onnistui:
ErrorRenamingTemp=Virhe uudelleennimett�ess� tiedostoa kohdehakemistossa:
ErrorRegisterServer=DLL/OCX -laajennuksen rekister�inti ep�onnistui: %1
ErrorRegSvr32Failed=RegSvr32-toiminto ep�onnistui. Virhekoodi: %1
ErrorRegisterTypeLib=Tyyppikirjaston rekister�iminen ep�onnistui: %1

; *** Uninstall display name markings
UninstallDisplayNameMark=%1 (%2)
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32-bittinen
UninstallDisplayNameMark64Bit=64-bittinen
UninstallDisplayNameMarkAllUsers=Kaikki k�ytt�j�t
UninstallDisplayNameMarkCurrentUser=T�m�nhetkinen k�ytt�j�

; *** Post-installation errors
ErrorOpeningReadme=Virhe avattaessa LUEMINUT-tiedostoa.
ErrorRestartingComputer=Koneen uudelleenk�ynnist�minen ei onnistunut. Suorita uudelleenk�ynnistys itse.

; *** Uninstaller messages
UninstallNotFound=Tiedostoa "%1" ei l�ytynyt. Asennuksen poisto ei onnistu.
UninstallOpenError=Tiedostoa "%1" ei voitu avata. Asennuksen poisto ei onnistu.
UninstallUnsupportedVer=T�m� versio Asennuksen poisto-ohjelmasta ei pysty lukemaan lokitiedostoa "%1". Asennuksen poisto ei onnistu
UninstallUnknownEntry=Asennuksen poisto-ohjelman lokitiedostosta l�ytyi tuntematon merkint� (%1)
ConfirmUninstall=Poistetaanko %1 ja kaikki sen osat?
UninstallOnlyOnWin64=T�m� ohjelma voidaan poistaa vain 64-bittisest� Windowsista k�sin.
OnlyAdminCanUninstall=T�m�n asennuksen poistaminen vaatii j�rjestelm�nvalvojan oikeudet.
UninstallStatusLabel=Odota, kun %1 poistetaan koneeltasi.
UninstalledAll=%1 poistettiin onnistuneesti.
UninstalledMost=%1 poistettiin koneelta.%n%nJoitakin osia ei voitu poistaa. Voit poistaa osat itse.
UninstalledAndNeedsRestart=Kone t�ytyy k�ynnist�� uudelleen, jotta %1 voidaan poistaa kokonaan.%n%nHaluatko k�ynnist�� koneen uudeelleen nyt?
UninstallDataCorrupted=Tiedosto "%1" on vaurioitunut. Asennuksen poisto ei onnistu.

; *** Uninstallation phase messages
ConfirmDeleteSharedFileTitle=Poistetaanko jaettu tiedosto?
ConfirmDeleteSharedFile2=J�rjestelm�n mukaan seuraava jaettu tiedosto ei ole en�� mink��n muun sovelluksen k�yt�ss�. Poistetaanko tiedosto?%n%nJos jotkut sovellukset k�ytt�v�t viel� t�t� tiedostoa ja se poistetaan, ne eiv�t v�ltt�m�tt� toimi en�� kunnolla. Jos olet ep�varma, valitse Ei. Tiedoston j�tt�minen koneelle ei aiheuta ongelmia.
SharedFileNameLabel=Tiedoston nimi:
SharedFileLocationLabel=Sijainti:
WizardUninstalling=Asennuksen poiston tila
StatusUninstalling=Poistetaan %1...

[CustomMessages]

NameAndVersion=%1 versio %2
AdditionalIcons=Lis�kuvakkeet:
CreateDesktopIcon=Lu&o kuvake ty�p�yd�lle
CreateQuickLaunchIcon=Luo kuvake &pikak�ynnistyspalkkiin
ProgramOnTheWeb=%1 Internetiss�
UninstallProgram=Poista %1
LaunchProgram=&K�ynnist� %1
AssocFileExtension=&Yhdist� %1 tiedostop��tteeseen %2
AssocingFileExtension=Yhdistet��n %1 tiedostop��tteeseen %2 ...
AutoStartProgramGroupDescription=K�ynnistys:
AutoStartProgram=K�ynnist� %1 automaattisesti
AddonHostProgramNotFound=%1 ei ole valitsemassasi kansiossa.%n%nHaluatko jatkaa t�st� huolimatta?
