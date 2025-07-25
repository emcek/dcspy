; *** Inno Setup version 6.4.0+ Bulgarian messages ***
; Ventsislav Dimitrov <nightravenanm@protonmail.com>
;
; За да изтеглите преводи на този файл, предоставени от потребители, посетете:
;   http://www.jrsoftware.org/files/istrans/
;
; Забележка: когато превеждате, не добавяйте точка (.) в края на съобщения,
; които нямат, защото Inno Setup им добавя автоматично (прибавянето на точка
; ще доведе до показване на две точки).

[LangOptions]
; Следните три записа са много важни. Уверете се, че сте прочел и разбирате
; раздела "[LangOptions]" на помощния файл.
LanguageName=Български
LanguageID=$0402
LanguageCodePage=1251
; Ако езикът, на който превеждате, изисква специална гарнитура или размер на
; шрифта, извадете от коментар съответните записи по-долу и ги променете
; според вашите нужди.
;DialogFontName=
;DialogFontSize=8
;WelcomeFontName=Verdana
;WelcomeFontSize=12
;TitleFontName=Arial
;TitleFontSize=29
;CopyrightFontName=Arial
;CopyrightFontSize=8

[Messages]

; *** Заглавия на приложенията
SetupAppTitle=Инсталиране
SetupWindowTitle=Инсталиране на %1
UninstallAppTitle=Деинсталиране
UninstallAppFullTitle=Деинсталиране на %1

; *** Заглавия от общ тип
InformationTitle=Информация
ConfirmTitle=Потвърждение
ErrorTitle=Грешка

; *** Съобщения на зареждащия модул
SetupLdrStartupMessage=Ще се инсталира %1. Желаете ли да продължите?
LdrCannotCreateTemp=Не е възможно да се създаде временен файл. Инсталирането бе прекратено
LdrCannotExecTemp=Не е възможно да се стартира файл от временната директория. Инсталирането бе прекратено

; *** Съобщения за грешка при стартиране
LastErrorMessage=%1.%n%nГрешка %2: %3
SetupFileMissing=Файлът %1 липсва от инсталационната директория. Моля, отстранете проблема или се снабдете с ново копие на програмата.
SetupFileCorrupt=Инсталационните файлове са повредени. Моля, снабдете се с ново копие на програмата.
SetupFileCorruptOrWrongVer=Инсталационните файлове са повредени или несъвместими с тази версия на инсталатора. Моля, отстранете проблема или се снабдете с ново копие на програмата.
InvalidParameter=В командния ред е подаден невалиден параметър:%n%n%1
SetupAlreadyRunning=Инсталаторът вече се изпълнява.
WindowsVersionNotSupported=Програмата не поддържа версията на Windows, с която работи компютърът ви.
WindowsServicePackRequired=Програмата изисква %1 Service Pack %2 или по-нов.
NotOnThisPlatform=Програмата не може да се изпълнява под %1.
OnlyOnThisPlatform=Програмата трябва да се изпълнява под %1.
OnlyOnTheseArchitectures=Програмата може да се инсталира само под версии на Windows за следните процесорни архитектури:%n%n%1
WinVersionTooLowError=Програмата изисква %1 версия %2 или по-нова.
WinVersionTooHighError=Програмата не може да бъде инсталирана в %1 версия %2 или по-нова.
AdminPrivilegesRequired=За да инсталирате програмата, трябва да влезете като администратор.
PowerUserPrivilegesRequired=За да инсталирате програмата, трябва да влезете като администратор или потребител с разширени права.
SetupAppRunningError=Инсталаторът установи, че %1 се изпълнява в момента.%n%nМоля, затворете всички копия на програмата и натиснете "OK", за да продължите, или "Cancel" за изход.
UninstallAppRunningError=Деинсталаторът установи, че %1 се изпълнява в момента.%n%nМоля, затворете всички копия на програмата и натиснете "OK", за да продължите, или "Cancel" за изход.

; *** Въпроси при стартиране
PrivilegesRequiredOverrideTitle=Избор на режим на инсталация
PrivilegesRequiredOverrideInstruction=Изберете режим на инсталация
PrivilegesRequiredOverrideText1=%1 може да бъде инсталирана за всички потребители (изисква администраторски привилегии) или само за Вас.
PrivilegesRequiredOverrideText2=%1 може да бъде инсталирана само за Вас или за всички потребители (изисква администраторски привилегии).
PrivilegesRequiredOverrideAllUsers=Инсталирай за &всички потребители
PrivilegesRequiredOverrideAllUsersRecommended=Инсталирай за &всички потребители (препоръчва се)
PrivilegesRequiredOverrideCurrentUser=Инсталирай само за &мен
PrivilegesRequiredOverrideCurrentUserRecommended=Инсталирай само за &мен (препоръчва се)

; *** Други грешки
ErrorCreatingDir=Не е възможно да се създаде директория "%1"
ErrorTooManyFilesInDir=Не е възможно да се създаде файл в директорията "%1", тъй като тя съдържа твърде много файлове

; *** Съобщения от общ тип на инсталатора
ExitSetupTitle=Затваряне на инсталатора
ExitSetupMessage=Инсталирането не е завършено. Ако затворите сега, програмата няма да бъде инсталирана.%n%nПо-късно можете отново да стартирате инсталатора, за да завършите инсталирането.%n%nЗатваряте ли инсталатора?
AboutSetupMenuItem=&За инсталатора...
AboutSetupTitle=За инсталатора
AboutSetupMessage=%1 версия %2%n%3%n%nУебстраница:%n%4
AboutSetupNote=
TranslatorNote=Превод на български: Михаил Балабанов

; *** Бутони
ButtonBack=< На&зад
ButtonNext=На&пред >
ButtonInstall=&Инсталиране
ButtonOK=OK
ButtonCancel=Отказ
ButtonYes=&Да
ButtonYesToAll=Да за &всички
ButtonNo=&Не
ButtonNoToAll=Не за в&сички
ButtonFinish=&Готово
ButtonBrowse=Пре&глед...
ButtonWizardBrowse=Пре&глед...
ButtonNewFolder=&Нова папка

; *** Съобщения в диалоговия прозорец за избор на език
SelectLanguageTitle=Избор на език за инсталатора
SelectLanguageLabel=Изберете кой език ще ползвате с инсталатора.

; *** Текстове от общ тип на съветника
ClickNext=Натиснете "Напред", за да продължите, или "Отказ" за затваряне на инсталатора.
BeveledLabel=
BrowseDialogTitle=Преглед за папка
BrowseDialogLabel=Изберете папка от долния списък и натиснете "OK".
NewFolderName=Нова папка

; *** Страница "Добре дошли" на съветника
WelcomeLabel1=Добре дошли при Съветника за инсталиране на [name]
WelcomeLabel2=Съветникът ще инсталира [name/ver] във Вашия компютър.%n%nПрепоръчва се да затворите всички останали приложения, преди да продължите.

; *** Страница "Лицензионно споразумение" на съветника
WizardLicense=Лицензионно споразумение
LicenseLabel=Моля, прочетете следната важна информация, преди да продължите.
LicenseLabel3=Моля, прочетете следното Лицензионно споразумение. Преди инсталирането да продължи, трябва да приемете условията на споразумението.
LicenseAccepted=П&риемам споразумението
LicenseNotAccepted=&Не приемам споразумението

; *** Страници "Информация" на съветника
WizardInfoBefore=Информация
InfoBeforeLabel=Моля, прочетете следната важна информация, преди да продължите.
InfoBeforeClickLabel=Когато сте готов да продължите, натиснете "Напред".
WizardInfoAfter=Информация
InfoAfterLabel=Моля, прочетете следната важна информация, преди да продължите.
InfoAfterClickLabel=Когато сте готов да продължите, натиснете "Напред".

; *** Страница "Данни за потребител" на съветника
WizardUserInfo=Данни за потребител
UserInfoDesc=Моля, въведете вашите данни.
UserInfoName=&Име:
UserInfoOrg=&Организация:
UserInfoSerial=&Сериен номер:
UserInfoNameRequired=Трябва да въведете име.

; *** Страница "Избор на местоназначение" на съветника
WizardSelectDir=Избор на местоназначение
SelectDirDesc=Къде да се инсталира [name]?
SelectDirLabel3=[name] ще се инсталира в следната папка.
SelectDirBrowseLabel=Натиснете "Напред", за да продължите. За да изберете друга папка, натиснете "Преглед".
DiskSpaceGBLabel=Изискват се поне [gb] ГБ свободно дисково пространство.
DiskSpaceMBLabel=Изискват се поне [mb] МБ свободно дисково пространство.
CannotInstallToNetworkDrive=Инсталаторът не може да инсталира на мрежово устройство.
CannotInstallToUNCPath=Инсталаторът не може да инсталира в UNC път.
InvalidPath=Трябва да въведете пълен път с буква на устройство, например:%n%nC:\APP%n%nили UNC път във вида:%n%n\\сървър\споделено място
InvalidDrive=Избраното от вас устройство или споделено UNC място не съществува или не е достъпно. Моля, изберете друго.
DiskSpaceWarningTitle=Недостиг на дисково пространство
DiskSpaceWarning=Инсталирането изисква %1 кБ свободно място, но на избраното устройство има само %2 кБ.%n%nЖелаете ли все пак да продължите?
DirNameTooLong=Твърде дълго име на папка или път.
InvalidDirName=Името на папка е невалидно.
BadDirName32=Имената на папки не могат да съдържат следните знаци:%n%n%1
DirExistsTitle=Папката съществува
DirExists=Папката:%n%n%1%n%nвече съществува. Желаете ли все пак да инсталирате в нея?
DirDoesntExistTitle=Папката не съществува
DirDoesntExist=Папката:%n%n%1%n%nне съществува. Желаете ли да бъде създадена?

; *** Страница "Избор на компоненти" на съветника
WizardSelectComponents=Избор на компоненти
SelectComponentsDesc=Кои компоненти да бъдат инсталирани?
SelectComponentsLabel2=Изберете компонентите, които желаете да инсталирате, и откажете нежеланите. Натиснете "Напред", когато сте готов да продължите.
FullInstallation=Пълна инсталация
; По възможност не превеждайте "Compact" като "Minimal" (има се предвид "Minimal" на Вашия език)
CompactInstallation=Компактна инсталация
CustomInstallation=Инсталация по избор
NoUninstallWarningTitle=Компонентите съществуват
NoUninstallWarning=Инсталаторът установи, че следните компоненти са вече инсталирани в компютърa:%n%n%1%n%nОтказването на тези компоненти няма да ги деинсталира.%n%nЖелаете ли все пак да продължите?
ComponentSize1=%1 кБ
ComponentSize2=%1 МБ
ComponentsDiskSpaceGBLabel=Направеният избор изисква поне [gb] ГБ дисково пространство.
ComponentsDiskSpaceMBLabel=Направеният избор изисква поне [mb] МБ дисково пространство.

; *** Страница "Избор на допълнителни задачи" на съветника
WizardSelectTasks=Избор на допълнителни задачи
SelectTasksDesc=Кои допълнителни задачи да бъдат изпълнени?
SelectTasksLabel2=Изберете кои допълнителни задачи желаете да се изпълнят при инсталиране на [name], след което натиснете "Напред".

; *** Страница "Избор на папка в менюто "Старт" на съветника
WizardSelectProgramGroup=Избор на папка в менюто "Старт"
SelectStartMenuFolderDesc=Къде да бъдат поставени преките пътища на програмата?
SelectStartMenuFolderLabel3=Инсталаторът ще създаде преки пътища в следната папка от менюто "Старт".
SelectStartMenuFolderBrowseLabel=Натиснете "Напред", за да продължите. За да изберете друга папка, натиснете "Преглед".
MustEnterGroupName=Трябва да въведете име на папка.
GroupNameTooLong=Твърде дълго име на папка или път.
InvalidGroupName=Името на папка е невалидно.
BadGroupName=Името на папка не може да съдържа следните знаци:%n%n%1
NoProgramGroupCheck2=И&нсталиране без папка в менюто "Старт"

; *** Страница "Готовност за инсталиране" на съветника
WizardReady=Готовност за инсталиране
ReadyLabel1=Инсталаторът е готов да инсталира [name] във Вашия компютър.
ReadyLabel2a=Натиснете "Инсталиране", за да продължите, или "Назад" за преглед или промяна на някои настройки.
ReadyLabel2b=Натиснете "Инсталиране", за да продължите с инсталирането.
ReadyMemoUserInfo=Данни за потребител:
ReadyMemoDir=Местоназначение:
ReadyMemoType=Тип инсталация:
ReadyMemoComponents=Избрани компоненти:
ReadyMemoGroup=Папка в менюто "Старт":
ReadyMemoTasks=Допълнителни задачи:

; *** Страница "TDownloadWizardPage" на съветника и DownloadTemporaryFile
DownloadingLabel=Изтегляне на допълнителни файлове...
ButtonStopDownload=&Спри изтеглянето
StopDownload=Сигурни ли сте, че искате да спрете изтеглянето?
ErrorDownloadAborted=Изтеглянето беше прекъснато
ErrorDownloadFailed=Изтеглянето беше неуспешно: %1 %2
ErrorDownloadSizeFailed=Неуспешно получаване на размер: %1 %2
ErrorFileHash1=Неуспешна контролна сума на файл: %1
ErrorFileHash2=Невалидна контролна сума на файл: очаквана %1, открита %2
ErrorProgress=Невалиден напредък: %1 of %2
ErrorFileSize=Невалиден размер на файл: очакван %1, открит %2

; *** Страница "TExtractionWizardPage" на съветника и Extract7ZipArchive
ExtractionLabel=Извличане на допълнителни файлове...
ButtonStopExtraction=&Спри извличането
StopExtraction=Сигурни ли сте, че искате да спрете извличането?
ErrorExtractionAborted=Прекратено извличане
ErrorExtractionFailed=Извличането беше неуспешно: %1

; *** Страница "Подготовка за инсталиране" на съветника
WizardPreparing=Подготовка за инсталиране
PreparingDesc=Инсталаторът се подготвя да инсталира [name] във Вашия компютър.
PreviousInstallNotCompleted=Инсталиране или премахване на предишна програма не е завършило. Рестартирайте компютъра, за да може процесът да завърши.%n%nСлед като рестартирате, стартирайте инсталатора отново, за да довършите инсталирането на [name].
CannotContinue=Инсталирането не може да продължи. Моля, натиснете "Отказ" за изход.
ApplicationsFound=Следните приложения използват файлове, които трябва да бъдат обновени от инсталатора. Препоръчва се да разрешите на инсталатора автоматично да затвори приложенията.
ApplicationsFound2=Следните приложения използват файлове, които трябва да бъдат обновени от инсталатора. Препоръчва се да разрешите на инсталатора автоматично да затвори приложенията. След края на инсталирането ще бъде направен опит за рестартирането им.
CloseApplications=Приложенията да се затворят &автоматично
DontCloseApplications=Приложенията да &не се затварят
ErrorCloseApplications=Не бе възможно да се затворят автоматично всички приложения. Препоръчва се преди да продължите, да затворите всички приложения, използващи файлове, които инсталаторът трябва да обнови.
PrepareToInstallNeedsRestart=Инсталаторът трябва да ресартира Вашия компютър. След рестартирането, стартирайте инсталатора отново, за да завършите инсталацията на [name].%n%nЖелаете ли да рестартирате сега?

; *** Страница "Инсталиране" на съветника
WizardInstalling=Инсталиране
InstallingLabel=Моля, изчакайте докато [name] се инсталира във Вашия компютър.

; *** Страница "Инсталирането завърши" на съветника
FinishedHeadingLabel=Съветникът за инсталиране на [name] завърши
FinishedLabelNoIcons=Инсталирането на [name] във Вашия компютър завърши.
FinishedLabel=Инсталирането на [name] във Вашия компютър завърши. Можете да стартирате приложението чрез инсталираните икони.
ClickFinish=Натиснете "Готово", за да затворите инсталатора.
FinishedRestartLabel=Инсталаторът трябва да рестартира компютъра, за да завърши инсталирането на [name]. Желаете ли да рестартирате сега?
FinishedRestartMessage=Инсталаторът трябва да рестартира компютъра, за да завърши инсталирането на [name].%n%nЖелаете ли да рестартирате сега?
ShowReadmeCheck=Да, желая да прегледам файла README
YesRadio=&Да, нека компютърът се рестартира сега
NoRadio=&Не, ще рестартирам компютъра по-късно
; Използва се например в "Стартиране на MyProg.exe"
RunEntryExec=Стартиране на %1
; Използва се например в "Преглеждане на Readme.txt"
RunEntryShellExec=Преглеждане на %1

; *** Текстове от рода на "Инсталаторът изисква следващ носител"
ChangeDiskTitle=Инсталаторът изисква следващ носител
SelectDiskLabel2=Моля, поставете носител %1 и натиснете "ОК".%n%nАко файловете от носителя се намират в различна от показаната по-долу папка, въведете правилния път до тях или натиснете "Преглед".
PathLabel=П&ът:
FileNotInDir2=Файлът "%1" не бе намерен в "%2". Моля, поставете правилния носител или изберете друга папка.
SelectDirectoryLabel=Моля, посочете местоположението на следващия носител.

; *** Съобщения от фаза "Инсталиране"
SetupAborted=Инсталирането не е завършено.%n%nМоля, отстранете проблема и стартирайте инсталатора отново.
AbortRetryIgnoreSelectAction=Изберете действие
AbortRetryIgnoreRetry=Повторен &опит
AbortRetryIgnoreIgnore=&Пренебрегни грешката и продължи
AbortRetryIgnoreCancel=Прекрати инсталацията

; *** Съобщения за хода на инсталирането
StatusClosingApplications=Затварят се приложения...
StatusCreateDirs=Създават се директории...
StatusExtractFiles=Извличат се файлове...
StatusCreateIcons=Създават се преки пътища...
StatusCreateIniEntries=Създават се записи в INI файл...
StatusCreateRegistryEntries=Създават се записи в регистъра...
StatusRegisterFiles=Регистрират се файлове...
StatusSavingUninstall=Записват се данни за деинсталиране...
StatusRunProgram=Инсталацията приключва...
StatusRestartingApplications=Рестартират се приложения...
StatusRollback=Заличават се промени...

; *** Грешки от общ тип
ErrorInternal2=Вътрешна грешка: %1
ErrorFunctionFailedNoCode=Неуспешно изпълнение на %1
ErrorFunctionFailed=Неуспешно изпълнение на %1; код на грешката: %2
ErrorFunctionFailedWithMessage=Неуспешно изпълнение на %1; код на грешката: %2.%n%3
ErrorExecutingProgram=Не е възможно да се стартира файл:%n%1

; *** Грешки, свързани с регистъра
ErrorRegOpenKey=Грешка при отваряне на ключ в регистъра:%n%1\%2
ErrorRegCreateKey=Грешка при създаване на ключ в регистъра:%n%1\%2
ErrorRegWriteKey=Грешка при писане в ключ от регистъра:%n%1\%2

; *** Грешки, свързани с INI файлове
ErrorIniEntry=Грешка при създаване на INI запис във файла "%1".

; *** Грешки при копиране на файлове
FileAbortRetryIgnoreSkipNotRecommended=Прескочи този &файл (не се препоръчва)
FileAbortRetryIgnoreIgnoreNotRecommended=&Пренебрегни грешката и продължи (не се препоръчва)
SourceIsCorrupted=Файлът - източник е повреден
SourceDoesntExist=Файлът - източник "%1" не съществува
ExistingFileReadOnly2=Съществуващият файл не беше заменен, защото е маркиран само за четене.
ExistingFileReadOnlyRetry=&Премахни атрибута „само за четене“ и опитай отново
ExistingFileReadOnlyKeepExisting=&Запази съществуващия файл
ErrorReadingExistingDest=Грешка при опит за четене на съществуващ файл:
FileExistsSelectAction=Изберете действие
FileExists2=Файлът вече съществува.
FileExistsOverwriteExisting=&Презапиши съществуващия файл
FileExistsKeepExisting=&Запази съществуващия файл
FileExistsOverwriteOrKeepAll=&Извършвай същото за останалите конфликти
ExistingFileNewerSelectAction=Изберете действие
ExistingFileNewer2=Съществуващият файл е по-нов от този, който инсталаторът се опитва да инсталира.
ExistingFileNewerOverwriteExisting=&Презапиши съществуващия файл
ExistingFileNewerKeepExisting=&Запази съществуващия файл (препоръчително)
ExistingFileNewerOverwriteOrKeepAll=&Извършвай същото за останалите конфликти
ErrorChangingAttr=Грешка при опит за смяна на атрибути на съществуващ файл:
ErrorCreatingTemp=Грешка при опит за създаване на файл в целевата директория:
ErrorReadingSource=Грешка при опит за четене на файл - източник:
ErrorCopying=Грешка при опит за копиране на файл:
ErrorReplacingExistingFile=Грешка при опит за заместване на съществуващ файл:
ErrorRestartReplace=Неуспешно отложено заместване:
ErrorRenamingTemp=Грешка при опит за преименуване на файл в целевата директория:
ErrorRegisterServer=Не е възможно да се регистрира библиотека от тип DLL/OCX: %1
ErrorRegSvr32Failed=Неуспешно изпълнение на RegSvr32 с код на изход %1
ErrorRegisterTypeLib=Не е възможно да се регистрира библиотека от типове: %1

; *** Обозначаване на показваните имена на програми за деинсталиране
UninstallDisplayNameMark=%1 (%2)
UninstallDisplayNameMarks=%1 (%2, %3)
UninstallDisplayNameMark32Bit=32-битова
UninstallDisplayNameMark64Bit=64-битова
UninstallDisplayNameMarkAllUsers=Всички потребители
UninstallDisplayNameMarkCurrentUser=Текущ потребител

; *** Грешки след инсталиране
ErrorOpeningReadme=Възникна грешка при опит за отваряне на файла README.
ErrorRestartingComputer=Инсталаторът не е в състояние да рестартира компютъра. Моля, направете го ръчно.

; *** Съобщения на деинсталатора
UninstallNotFound=Файлът "%1" не съществува. Деинсталирането е невъзможно.
UninstallOpenError=Файлът "%1" не може да се отвори. Деинсталирането е невъзможно
UninstallUnsupportedVer=Форматът на регистрационния файл за деинсталиране "%1" не се разпознава от тази версия на деинсталатора. Деинсталирането е невъзможно
UninstallUnknownEntry=Открит бе непознат запис (%1) в регистрационния файл за деинсталиране
ConfirmUninstall=Наистина ли желаете да премахнете напълно %1 и всички прилежащи компоненти?
UninstallOnlyOnWin64=Програмата може да бъде деинсталирана само под 64-битов Windows.
OnlyAdminCanUninstall=Програмата може да бъде премахната само от потребител с администраторски права.
UninstallStatusLabel=Моля, изчакайте премахването на %1 от Вашия компютър да приключи.
UninstalledAll=%1 беше премахната успешно от Вашия компютър.
UninstalledMost=Деинсталирането на %1 завърши.%n%nПремахването на някои елементи не бе възможно. Можете да ги отстраните ръчно.
UninstalledAndNeedsRestart=За да приключи деинсталирането на %1, трябва да рестартирате Вашия компютър.%n%nЖелаете ли да рестартирате сега?
UninstallDataCorrupted=Файлът "%1" е повреден. Деинсталирането е невъзможно

; *** Съобщения от фаза "Деинсталиране"
ConfirmDeleteSharedFileTitle=Премахване на споделен файл?
ConfirmDeleteSharedFile2=Системата отчита, че следният споделен файл вече не се ползва от никоя програма. Желаете ли деинсталаторът да го премахне?%n%nАко някоя програма все пак ползва файла и той бъде изтрит, програмата може да спре да работи правилно. Ако се колебаете, изберете "Не". Оставянето на файла в системата е безвредно.
SharedFileNameLabel=Име на файла:
SharedFileLocationLabel=Местоположение:
WizardUninstalling=Ход на деинсталирането
StatusUninstalling=%1 се деинсталира...

; *** Обяснения за блокирано спиране на системата
ShutdownBlockReasonInstallingApp=Инсталира се %1.
ShutdownBlockReasonUninstallingApp=Деинсталира се %1.

; Потребителските съобщения по-долу не се ползват от самия инсталатор, но
; ако ползвате такива в скриптовете си, вероятно бихте искали да ги преведете.

[CustomMessages]

NameAndVersion=%1, версия %2
AdditionalIcons=Допълнителни икони:
CreateDesktopIcon=Икона на &работния плот
CreateQuickLaunchIcon=Икона в лентата "&Бързо стартиране"
ProgramOnTheWeb=%1 в Интернет
UninstallProgram=Деинсталиране на %1
LaunchProgram=Стартиране на %1
AssocFileExtension=&Свързване на %1 с файловото разширение %2
AssocingFileExtension=%1 се свързва с файловото разширение %2...
AutoStartProgramGroupDescription=Стартиране:
AutoStartProgram=Автоматично стартиране на %1
AddonHostProgramNotFound=%1 не бе намерена в избраната от вас папка.%n%nЖелаете ли все пак да продължите?
