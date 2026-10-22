"""Hash a slide and its render dependencies, excluding nonvisual notes."""

import hashlib
import json
import os
import platform
import zipfile
from pathlib import Path

from .source_deck import NS, _part_relative, _rels_path, _xml


def environment_key():
    fonts=[]
    for directory in (Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts',
                      Path(os.environ.get('LOCALAPPDATA','.'))/'Microsoft/Windows/Fonts'):
        if directory.is_dir():
            for path in directory.iterdir():
                try:
                    state=path.stat()
                    fonts.append((path.name,state.st_size,state.st_mtime_ns))
                except OSError:
                    continue
    office=[]
    if os.name=='nt':
        import winreg
        for root in (winreg.HKEY_LOCAL_MACHINE,winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(root,r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\POWERPNT.EXE') as key:
                    executable=Path(winreg.QueryValue(key,None).strip('"'))
                    state=executable.stat()
                    office.append((str(executable),state.st_size,state.st_mtime_ns))
            except OSError:
                continue
    return hashlib.sha256(json.dumps({'engine':7,'machine':platform.node(),
                                     'fonts':sorted(fonts),'office':office},
                                    sort_keys=True).encode()).hexdigest()


class SlideFingerprints:
    def __init__(self,path):
        self.path=Path(path)
        self.parts={}
        self.unsafe=set()
        self.available=zipfile.is_zipfile(path)

    def keys(self):
        if not self.available:
            return None
        result={}
        try:
            with zipfile.ZipFile(self.path) as archive:
                names=set(archive.namelist())
                presentation=_xml(archive.read('ppt/presentation.xml'))
                relationships=_xml(archive.read('ppt/_rels/presentation.xml.rels'))
                slides={node.get('Id'):_part_relative('ppt/presentation.xml',node.get('Target',''))
                        for node in relationships if node.get('Type','').endswith('/slide')}
                context=hashlib.sha256(archive.read('ppt/presentation.xml')+archive.read('ppt/_rels/presentation.xml.rels')).hexdigest()

                def dependencies(part,seen):
                    if part in seen:
                        return True
                    seen.add(part)
                    if part in self.unsafe:
                        return False
                    if part not in self.parts:
                        data=archive.read(part)
                        self.parts[part]=hashlib.sha256(data).hexdigest()
                        if part.endswith('.xml') and b'datetime' in data.lower() and b':fld' in data:
                            dynamic=[node for node in _xml(data).iter() if node.tag.rsplit('}',1)[-1]=='fld'
                                     and 'datetime' in node.get('type','').lower()]
                            if dynamic and (part.startswith('ppt/slides/') or any(':' in ''.join(node.itertext()) for node in dynamic)):
                                self.unsafe.add(part)
                                return False
                            for field in dynamic:
                                shape = next((node for node in field.iterancestors()
                                              if node.tag == '{' + NS['p'] + '}sp'), None)
                                placeholder = shape.find('p:nvSpPr/p:nvPr/p:ph', NS) if shape is not None else None
                                if placeholder is None or placeholder.get('type') != 'dt':
                                    self.unsafe.add(part)
                                    return False
                            # Footer date placeholders may be hidden on this slide.
                            # Native rendering records whether the date is actually
                            # visible; RenderCache expires only those pages daily.
                    relationships=_rels_path(part)
                    if relationships not in names:
                        return True
                    tree=_xml(archive.read(relationships))
                    visible=[]
                    for node in tree:
                        kind=node.get('Type','').rsplit('/',1)[-1]
                        if kind in {'notesSlide','notesMaster','comments','tags'}:
                            continue
                        visible.append(sorted(node.attrib.items()))
                        if node.get('TargetMode')=='External':
                            if kind!='hyperlink':
                                return False
                        elif not dependencies(_part_relative(part,node.get('Target','')),seen):
                            return False
                    self.parts[relationships]=hashlib.sha256(json.dumps(visible,sort_keys=True).encode()).hexdigest()
                    seen.add(relationships)
                    return True

                for index,node in enumerate(presentation.find('p:sldIdLst',NS),1):
                    seen=set()
                    part=slides[node.get('{'+NS['r']+'}id')]
                    complete=dependencies(part,seen)
                    result[str(index)]=(hashlib.sha256(json.dumps({'slide':index,'presentation':context,
                        'parts':[(name,self.parts[name]) for name in sorted(seen)]},sort_keys=True).encode()).hexdigest()
                        if complete else None)
        except (OSError,ValueError,KeyError,TypeError,AttributeError,zipfile.BadZipFile):
            return {}
        return result
