import sys

from bs4 import BeautifulSoup
import requests
import pywhatkit
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import timedelta , datetime
path = "chromedriver.exe"

from selenium import webdriver

jam_pengiriman = ['08','12','16','20']

#AMBIL DATA NAMA SITE
##SEISMOMTER
site = open("site_balikpapan.txt", 'r')
siesmo = site.readline().replace("\n","")
seismo = siesmo.split(" ")
##ACCELERO COLOCATED
acceleroColocated = site.readline().replace("\n", "")
acceleroColocated = acceleroColocated.split(" ")
##ACCELERO NONCOLOCATED
acceleroNonColocated = site.readline().replace("\n","")
acceleroNonColocated=acceleroNonColocated.split(" ")
site.close()

##inisiasikan site off
siteOff = []


#=========================CEK KONDISI SIESMOTER============================#
sensoroff_seis= []
sensoroff_seis_latency= []
jumlah_on_seis = 0
jumlah_off_seis = 0
for site in seismo :
  link = "http://202.90.198.40/sismon-wrs/web/detail_slmon2/" + site
  webpage = requests.get(link)
  soup = BeautifulSoup(webpage.content, "html.parser")
  ## masukan string = 1 untuk mengecek data SHZ
  data = soup.find(string='1')
  data = data.find_parent("tr").text
  data = ' '.join(data.split())
  data1 = data.split(' ')
  kodesensor = data1[1]
  latency = data1[len(data1) - 1]
  lat = ""
  satuan = ""
  # print(site)
  for c in latency:
    if c.isdigit():
      lat = lat + c
    else:
      satuan = satuan + c

  waktu = int(lat)
  if satuan == 's':
    status = 'ON'
    jumlah_on_seis = jumlah_on_seis + 1
  elif waktu < 10 and satuan == 'm':
    status = 'ON'
    jumlah_on_seis = jumlah_on_seis + 1
  else:
    status = 'OFF'
    jumlah_off_seis = jumlah_off_seis + 1
    sensoroff_seis_latency.append(site + " " + str(waktu) + " " + satuan)
    sensoroff_seis.append(site)
    siteOff.append(site)


jumlah_sensor_seis= len(seismo)

#=========================CEK KONDISI ACCELERO COLOCATED==============================#
sensoroff_acc= []
sensoroff_acc_latency= []
jumlah_on_acc = 0
jumlah_off_acc = 0
for site in acceleroColocated :
  link = "http://202.90.198.40/sismon-wrs/web/detail_slmon2/" + site
  webpage = requests.get(link)
  soup = BeautifulSoup(webpage.content, "html.parser")
  ## masukan string = 4 untuk mengecek data HNZ
  data = soup.find(string='4')
  data = data.find_parent("tr").text
  data = ' '.join(data.split())
  data1 = data.split(' ')
  kodesensor = data1[1]
  latency = data1[len(data1) - 1]
  lat = ""
  satuan = ""
  # print(site)
  if latency == "NA":
    status = 'OFF'
    jumlah_off_acc = jumlah_off_acc + 1
    sensoroff_acc_latency.append(site + " " + satuan)
    sensoroff_acc.append(site)
    siteOff.append(site)
    continue
  for c in latency:
    if c.isdigit():
      lat = lat + c
    else:
      satuan = satuan + c

  waktu = int(lat)
  if satuan == 's':
    status = 'ON'
    jumlah_on_acc = jumlah_on_acc + 1

  elif waktu < 10 and satuan == 'm':
    status = 'ON'
    jumlah_on_acc = jumlah_on_acc + 1
  else:
    status = 'OFF'
    jumlah_off_acc = jumlah_off_acc + 1
    sensoroff_acc_latency.append(site + " " + str(waktu) + " " + satuan)
    sensoroff_acc.append(site)
    siteOff.append(site)

jumlah_sensor_acc = len(acceleroColocated)

#=======================ACCELEROMETER NONCOLO================================#
driver = webdriver.Chrome()
driver.get("https://simora.bmkg.go.id/simora/web/login_page")
username = 'stageof.balikpapan'
password = '12345678'

try:
    cek = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.NAME,"login"))
    )
    driver.find_element("name", "username").send_keys(username)
    driver.find_element("name", "password").send_keys(password)
    driver.find_element("name", "login").click()
except:
    driver.close()

sensoroff_acc_noncolo= []
sensoroff_acc_noncolo_latency= []
jumlah_on_acc_noncolo = 0
jumlah_off_acc_noncolo = 0

driver.get("https://simora.bmkg.go.id/simora/simora_upt/status_acc2")
select = Select(driver.find_element(By.NAME, "example_length"))
select.select_by_value('100')


try:
    cek2 = WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.XPATH,f'//td[text()="{acceleroNonColocated[1]}"]'))
    )
    # test = driver.find_element(By.XPATH,f'//td[text()={sensor}]')
    # test2 = test.find_element(By.XPATH,"..")
    # print(test2.text)
    for site in acceleroNonColocated:
        s = driver.find_element(By.XPATH,f'//td[text()="{site}"]')
        s1 = s.find_element(By.XPATH,"..")
        s2 = ' '.join(s1.text.split())
        s2 = s2.split(" ")[1]
        lastData = s2
        lastData = lastData.replace("T", " ")
        date_format = '%Y-%m-%d %H:%M:%S'
        lastData = datetime.strptime(lastData, date_format)
        now = datetime.now() - timedelta(hours=8)
        latency = now - lastData
        latencyInHour = round(latency.total_seconds() / 3600, 1)
        if latencyInHour > 1:
            latency = round(latency.total_seconds() / 3600, 1)
            satuan = "h"
        else:
            latency = round(latency.total_seconds() / 60, 1)
            satuan = "m"

        # print(site , latency, satuan)
        if satuan == "m" and latency < 40:
          status = 'ON'
          jumlah_on_acc_noncolo = jumlah_on_acc_noncolo +1
        else:
          status = 'OFF'
          jumlah_off_acc_noncolo = jumlah_off_acc_noncolo + 1
          sensoroff_acc_noncolo_latency.append(site + " " + str(latency) + " " + satuan)
          sensoroff_acc_noncolo.append(site)
          siteOff.append(site)
except:
    print("tidak ditemukan")
jumlah_sensor_acc_noncolo= len(acceleroNonColocated)

driver.close()

##CETAK LAPORAN
laporan = f"""Izin Pimpinan, Izin melaporkan status Aloptama Stageof Balikpapan
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

STATUS SEISMOMETER
Jumlah Sensor : {jumlah_sensor_seis}
ON : {jumlah_on_seis}
OFF : {jumlah_off_seis} 
Sensor OFF : {sensoroff_seis_latency}

STATUS ACCELEROMETER
Jumlah Sensor : {jumlah_sensor_acc}
ON : {jumlah_on_acc}
OFF : {jumlah_off_acc} 
Sensor OFF : {sensoroff_acc_latency}

STATUS ACCELEROMETER NON COLOCATED
Jumlah Sensor : {jumlah_sensor_acc_noncolo}
ON : {jumlah_on_acc_noncolo}
OFF : {jumlah_off_acc_noncolo} 
Sensor OFF : {sensoroff_acc_noncolo_latency}

"""

## CEK SITE YANG OFF DARI DATA SEBELUMNYA
print(laporan)
z = open("siteOff.txt",'r')
siteOffYanglama2 = z.readline().replace("\n","")
siteOffYanglama2 = siteOffYanglama2.split(" ")
z.close()
siteOffYangLama = []
for x in siteOffYanglama2:
  if x != "":
    siteOffYangLama.append(x)


##UPDATE SITE OFF
siteYangOff = ""
for a in siteOff:
  siteYangOff = siteYangOff + a + " "
f = open("siteOff.txt", "w")
f.write(siteYangOff)
f.close()

##Ambil kode group
WA = open("kode_group.txt", 'r')
kode_group = WA.readline().replace("\n","")
kode_group = kode_group.split(" ")
WA.close()

##PROSES PENGIRIMAN LAPORAN Whatsapp
if (siteOff == siteOffYangLama):
  print("TIDAK ADA PERUBAHAN")
  f = open("status.txt", "w")
  f.write(laporan)
  f.close()
else:
  print("ADA PERUBAHAN !!!")
  f = open("status.txt", "w")
  f.write(laporan)
  f.close()
  pywhatkit.sendwhatmsg_to_group_instantly(kode_group[0],laporan,15,True,3,)
  sys.exit()

jam_sekarang = datetime.now().strftime("%H")

try:
  a = jam_pengiriman.index(jam_sekarang)
  f = open("status.txt", "w")
  f.write(laporan)
  f.close()
  print("WAKTU PENGIRIMAN")
  pywhatkit.sendwhatmsg_to_group_instantly(kode_group[0],laporan,15,True,3,)

except:
  print("bukan jam kirim")
