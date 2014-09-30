from xml.etree import ElementTree as ET

class parser():
    #Parsea el archivo de configuracion, mas detalles en el informe.
    def parseConfig(self): 
       lang = ET.parse('config.xml')

       ntwsc=lang.getroot().getchildren()[0].getchildren()
       result={}
       
       for sn in ntwsc:
          key=[]
          for keys in sn.getchildren():
             key.append(keys.attrib['key'])
          result[sn.tag]=key
            
       return result
