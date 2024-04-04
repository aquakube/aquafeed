# kube-feed


## Development

Frontend:
```
cd app
npm install
npm run start
```

Backend:
```
cd server
pipenv install
pipenv shell

CONTROLS_PLC_URL="http://controls.plc.svc.cluster.local:5000/api/plc" \
TIMEOUT_MAIN_PHASE_COMPLETED="30" \
CONTROL_LOOP_SLEEP_PERIOD_MAIN_PHASE="0.5" \
KAFKA_BROKERS="10.0.9.21:30130" \
FEED_STRINGS="[{'name':'portfs','title':'Port Feed String','location':'port','cage':'50B-2021','cohort':'SR-C06A22Ec_C06B','diet':{'diameter':'1.5 mm','brand':'Biomar','formula':'EFICO Sigma 2000','medicated':True},'augers':[{'metadata':{'make':'Marathon','model':'5K49SN4231AY','type':'Electric Motor','power':'1.5HP / 1.1kW','hz':'60Hz','phases':3,'voltage':'208-230/460 VAC','speed':'1725 RPM','diameter':'3 inch'},'settings':{'offSpeedThreshold':5,'feedRate':{'min':0,'max':100,'default':50,'pulseThreshold':30,'numberOfPulsesPerMinute':3}}}],'supplyPump':{'metadata':{'make':'DAE Pumps','model':'H440','type':'Self-Priming','power':'10HP / 7.5kW','hz':'60Hz','phases':3,'voltage':'208-230/460VAC','speed':'1800 RPM'},'settings':{'setupSpeed':100,'runSpeed':59,'offSpeedThreshold':5,'primeTimeout':120,'psiThresholds':{'min':-14,'max':0,'primed':-5}}},'deliveryPump':{'metadata':{'make':'Vaughan','model':'HSC4DHCS','type':'Centrifugal Transfer Pump','power':'10HP / 7.5kW','hz':'60Hz','phases':3,'voltage':'208-230/460VAC','speed':'1765 RPM'},'settings':{'runSpeed':100,'offSpeedThreshold':5,'shutoffPressureTimeout':30,'psiThresholds':{'min':10,'max':34}}},'mixingBowl':{'metadata':{'diameter':60,'volume':100},'settings':{'fillTimeout':6,'stabilizationTimeout':60,'flushTimeout':10,'minimumLevelMainPhase':8}},'hopper':{'metadata':{'diameter':60,'volume':100},'settings':{'timeLimit':60,'feedAmount':{'min':0,'max':1000,'default':250}}},'plc':{'metadata':{'make':'automation-direct','model':'C2-03CPU'},'settings':{'href':'http://portfs.plc.svc.cluster.local:5000/api/plc','timeout':0.5}},'calibrations':{'ratio_of_ticks_per_kg':521,'auger_run_speed_coefficients':{'a':0,'b':0.25,'c':12.5},'feed_rate_actual_coefficients':{'d':0,'e':0.25,'f':12.5}}},{'name':'starboardfs','title':'Starboard Feed String','location':'starboard','cage':'30K-2023','cohort':'SR-C06A22Ec_C06A','diet':{'diameter':'12 mm','brand':'Biomar','formula':'EFICO Sigma 2000','medicated':False},'augers':[{'metadata':{'make':'Marathon','model':'5K49SN4231AY','type':'Electric Motor','power':'1.5HP / 1.1kW','hz':'60Hz','phases':3,'voltage':'208-230/460 VAC','speed':'1725 RPM','diameter':'4 inch'},'settings':{'offSpeedThreshold':5,'feedRate':{'min':0,'max':100,'default':40,'pulseThreshold':30,'numberOfPulsesPerMinute':3}}},{'metadata':{'make':'Marathon','model':'5K49SN4231AY','type':'Electric Motor','power':'1.5HP / 1.1kW','hz':'60Hz','phases':3,'voltage':'208-230/460 VAC','speed':'1725 RPM','diameter':'4 inch'},'settings':{'offSpeedThreshold':5,'feedRate':{'min':0,'max':100,'default':40,'pulseThreshold':30,'numberOfPulsesPerMinute':3}}}],'supplyPump':{'metadata':{'make':'Pacer','model':'SE-2FV-CT','type':'Self-Priming','power':'5HP / 3.75kW','hz':'60Hz','phases':3,'voltage':'208-230/460VAC','speed':'3450 RPM'},'settings':{'setupSpeed':100,'runSpeed':59,'offSpeedThreshold':5,'primeTimeout':120,'psiThresholds':{'min':-14,'max':0,'primed':-5}}},'deliveryPump':{'metadata':{'make':'Vaughan','model':'HSC4DHCS','type':'Centrifugal Transfer Pump','power':'10HP / 7.5kW','hz':'60Hz','phases':3,'voltage':'208-230/460VAC','speed':'1765 RPM'},'settings':{'runSpeed':100,'offSpeedThreshold':5,'shutoffPressureTimeout':30,'psiThresholds':{'min':10,'max':34}}},'mixingBowl':{'metadata':{'diameter':60,'volume':100},'settings':{'fillTimeout':6,'stabilizationTimeout':60,'flushTimeout':10,'minimumLevelMainPhase':8}},'hopper':{'metadata':{'diameter':60,'volume':100},'settings':{'timeLimit':120,'feedAmount':{'min':0,'max':5000,'default':2500}}},'plc':{'metadata':{'make':'automation-direct','model':'C2-03CPU'},'settings':{'href':'http://stbdfs.plc.svc.cluster.local:5000/api/plc','timeout':0.5}},'calibrations':{'ratio_of_ticks_per_kg':521,'auger_run_speed_coefficients':{'a':0,'b':0.25,'c':12.5},'feed_rate_actual_coefficients':{'d':0,'e':0.25,'f':12.5}}}]" \
python3 src/main.py

```




```
CONTROLS_PLC_URL="http://10.0.9.21:31948/api/plc" \
TIMEOUT_MAIN_PHASE_COMPLETED="30" \
HTTP_PORT="5000" \
CONTROL_LOOP_SLEEP_PERIOD_MAIN_PHASE="0.5" \
KAFKA_BROKERS="10.0.9.21:30130" \
FEED_STRINGS="[{'name':'starboard','title':'Starboard Feed String','location':'starboard','cage':'50B-2021','cohort':'SR-C06A22Ec_C06B','diet':{'diameter':'1.5 mm','brand':'Biomar','formula':'EFICO Sigma 2000','medicated':True},'augers':[{'metadata':{'make':'Marathon','model':'5K49SN4231AY','type':'Electric Motor','power':'1.5HP / 1.1kW','hz':'60Hz','phases':3,'voltage':'208-230/460 VAC','speed':'1725 RPM','diameter':'3 inch'},'settings':{'offSpeedThreshold':5,'feedRate':{'min':0,'max':47,'default':40,'pulseThreshold':0,'numberOfPulsesPerMinute':3}}}],'supplyPump':{'metadata':{'make':'DAE Pumps','model':'H440','type':'Self-Priming','power':'10HP / 7.5kW','hz':'60Hz','phases':3,'voltage':'208-230/460VAC','speed':'1800 RPM'},'settings':{'setupSpeed':100,'runSpeed':100,'offSpeedThreshold':5,'primeTimeout':120,'psiThresholds':{'min':-14,'max':0,'primed':-5}}},'deliveryPump':{'metadata':{'make':'Vaughan','model':'HSC4DHCS','type':'Centrifugal Transfer Pump','power':'10HP / 7.5kW','hz':'60Hz','phases':3,'voltage':'208-230/460VAC','speed':'1765 RPM'},'settings':{'runSpeed':60,'offSpeedThreshold':5,'shutoffPressureTimeout':30,'psiThresholds':{'min':10,'max':34}}},'mixingBowl':{'metadata':{'diameter':60,'volume':100},'settings':{'fillTimeout':6,'stabilizationTimeout':60,'flushTimeout':10,'emptyBowlTimeout': 20,'minimumLevelMainPhase':8}},'hopper':{'metadata':{'diameter':60,'volume':100},'settings':{'timeLimit':60,'feedAmount':{'min':0,'max':1000,'default':250}}},'plc':{'metadata':{'make':'automation-direct','model':'C2-03CPU'},'settings':{'href':'http://10.0.9.21:30630/api/plc','timeout':1.5}},'calibrations':{'ratio_of_ticks_per_kg':31,'auger_run_speed_coefficients':{'a':74.9,'b':59.5,'c':8.72},'feed_rate_actual_coefficients':{'d':0,'e':0.00758,'f':0.0477}}},{'name':'port','title':'Port Feed String','location':'port','cage':'30K-2023','cohort':'SR-C06B22Ec_C06A','diet':{'diameter':'12 mm','brand':'Biomar','formula':'EFICO Sigma 2000','medicated':False},'augers':[{'metadata':{'make':'Marathon','model':'5K49SN4231AY','type':'Electric Motor','power':'1.5HP / 1.1kW','hz':'60Hz','phases':3,'voltage':'208-230/460 VAC','speed':'1725 RPM','diameter':'4 inch'},'settings':{'offSpeedThreshold':5,'feedRate':{'min':0,'max':100,'default':40,'pulseThreshold':30,'numberOfPulsesPerMinute':3}}},{'metadata':{'make':'Marathon','model':'5K49SN4231AY','type':'Electric Motor','power':'1.5HP / 1.1kW','hz':'60Hz','phases':3,'voltage':'208-230/460 VAC','speed':'1725 RPM','diameter':'4 inch'},'settings':{'offSpeedThreshold':5,'feedRate':{'min':0,'max':100,'default':40,'pulseThreshold':30,'numberOfPulsesPerMinute':3}}}],'supplyPump':{'metadata':{'make':'Pacer','model':'SE-2FV-CT','type':'Self-Priming','power':'5HP / 3.75kW','hz':'60Hz','phases':3,'voltage':'208-230/460VAC','speed':'3450 RPM'},'settings':{'setupSpeed':100,'runSpeed':59,'offSpeedThreshold':5,'primeTimeout':120,'psiThresholds':{'min':-14,'max':0,'primed':-5}}},'deliveryPump':{'metadata':{'make':'Vaughan','model':'HSC4DHCS','type':'Centrifugal Transfer Pump','power':'10HP / 7.5kW','hz':'60Hz','phases':3,'voltage':'208-230/460VAC','speed':'1765 RPM'},'settings':{'runSpeed':100,'offSpeedThreshold':5,'shutoffPressureTimeout':30,'psiThresholds':{'min':10,'max':34}}},'mixingBowl':{'metadata':{'diameter':60,'volume':100},'settings':{'fillTimeout':6,'stabilizationTimeout':60,'flushTimeout':10,'emptyBowlTimeout': 20,'minimumLevelMainPhase':8}},'hopper':{'metadata':{'diameter':60,'volume':100},'settings':{'timeLimit':120,'feedAmount':{'min':0,'max':5000,'default':2500}}},'plc':{'metadata':{'make':'automation-direct','model':'C2-03CPU'},'settings':{'href':'http://stbdfs.plc.svc.cluster.local:5000/api/plc','timeout':0.5}},'calibrations':{'ratio_of_ticks_per_kg':521,'auger_run_speed_coefficients':{'a':0,'b':0.25,'c':12.5},'feed_rate_actual_coefficients':{'d':0,'e':0.25,'f':12.5}}}]" \
python3 src/main.py

```