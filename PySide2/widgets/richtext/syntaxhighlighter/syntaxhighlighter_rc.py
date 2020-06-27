# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 5.15.0
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore

qt_resource_data = b"\
\x00\x00\x06\xca\
T\
EMPLATE = app\x0d\x0aL\
ANGUAGE = C++\x0d\x0aT\
ARGET         = \
assistant\x0d\x0a\x0d\x0aCON\
FIG        += qt\
 warn_on\x0d\x0aQT    \
        += xml n\
etwork\x0d\x0a\x0d\x0aPROJEC\
TNAME        = A\
ssistant\x0d\x0aDESTDI\
R            = .\
./../bin\x0d\x0a\x0d\x0aFORM\
S += finddialog.\
ui \x5c\x0d\x0a        he\
lpdialog.ui \x5c\x0d\x0a \
       mainwindo\
w.ui \x5c\x0d\x0a        \
settingsdialog.u\
i \x5c\x0d\x0a        tab\
bedbrowser.ui \x5c\x0d\
\x0a        topicch\
ooser.ui\x0d\x0a\x0d\x0aSOUR\
CES += main.cpp \
\x5c\x0d\x0a        helpw\
indow.cpp \x5c\x0d\x0a   \
     topicchoose\
r.cpp \x5c\x0d\x0a       \
 docuparser.cpp \
\x5c\x0d\x0a        setti\
ngsdialog.cpp \x5c\x0d\
\x0a        index.c\
pp \x5c\x0d\x0a        pr\
ofile.cpp \x5c\x0d\x0a   \
     config.cpp \
\x5c\x0d\x0a        findd\
ialog.cpp \x5c\x0d\x0a   \
     helpdialog.\
cpp \x5c\x0d\x0a        m\
ainwindow.cpp \x5c\x0d\
\x0a        tabbedb\
rowser.cpp\x0d\x0a\x0d\x0aHE\
ADERS        += \
helpwindow.h \x5c\x0d\x0a\
        topiccho\
oser.h \x5c\x0d\x0a      \
  docuparser.h \x5c\
\x0d\x0a        settin\
gsdialog.h \x5c\x0d\x0a  \
      index.h \x5c\x0d\
\x0a        profile\
.h \x5c\x0d\x0a        fi\
nddialog.h \x5c\x0d\x0a  \
      helpdialog\
.h \x5c\x0d\x0a        ma\
inwindow.h \x5c\x0d\x0a  \
      tabbedbrow\
ser.h \x5c\x0d\x0a       \
 config.h\x0d\x0a\x0d\x0aRES\
OURCES += assist\
ant.qrc\x0d\x0a\x0d\x0aDEFIN\
ES += QT_KEYWORD\
S\x0d\x0a#DEFINES +=  \
QT_PALMTOPCENTER\
_DOCS\x0d\x0a!network:\
DEFINES        +\
= QT_INTERNAL_NE\
TWORK\x0d\x0aelse:QT +\
= network\x0d\x0a!xml:\
 DEFINES        \
        += QT_IN\
TERNAL_XML\x0d\x0aelse\
:QT += xml\x0d\x0aincl\
ude( ../../src/q\
t_professional.p\
ri )\x0d\x0a\x0d\x0awin32 {\x0d\
\x0a    LIBS += -ls\
hell32\x0d\x0a    RC_F\
ILE = assistant.\
rc\x0d\x0a}\x0d\x0a\x0d\x0amacos {\
\x0d\x0a    ICON = ass\
istant.icns\x0d\x0a   \
 TARGET = assist\
ant\x0d\x0a#    QMAKE_\
INFO_PLIST = Inf\
o_mac.plist\x0d\x0a}\x0d\x0a\
\x0d\x0a#target.path =\
 $$[QT_INSTALL_B\
INS]\x0d\x0a#INSTALLS \
+= target\x0d\x0a\x0d\x0a#as\
sistanttranslati\
ons.files = *.qm\
\x0d\x0a#assistanttran\
slations.path = \
$$[QT_INSTALL_TR\
ANSLATIONS]\x0d\x0a#IN\
STALLS += assist\
anttranslations\x0d\
\x0a\x0d\x0aTRANSLATIONS \
       = assista\
nt_de.ts \x5c\x0d\x0a    \
              as\
sistant_fr.ts\x0d\x0a\x0d\
\x0a\x0d\x0aunix:!contain\
s(QT_CONFIG, zli\
b):LIBS += -lz\x0d\x0a\
\x0d\x0a\x0d\x0atarget.path=\
$$[QT_INSTALL_BI\
NS]\x0d\x0aINSTALLS +=\
 target\x0d\x0a\
"

qt_resource_name = b"\
\x00\x08\
\x0e\x84\x7fC\
\x00e\
\x00x\x00a\x00m\x00p\x00l\x00e\x00s\
\x00\x07\
\x0c\xe8G\xe5\
\x00e\
\x00x\x00a\x00m\x00p\x00l\x00e\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x16\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01rR\x22\xae\x00\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
