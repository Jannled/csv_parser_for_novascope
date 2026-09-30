# CSV Parser for Finapres® Novascope

This library was developed at my research institute to read in the CSV files exported by
the noninvasive continuous blood pressure monitor Finapres® Novascope to evaluate the data
for our studies and papers.

It uses [Pandas](https://pandas.pydata.org/docs/user_guide/index.html) under the hood,
which will simplify creating statistics for large amounts of data.

## Example

```python
data: dict[NOVASCOPE_TYPES, pd.Series] = dict(
	load_finapres(
		fc.selected,
		whitelist=['reBAP', 'Markers']
	)
)
```

The library will `yield` individual `pd.Series` objects. If you have issues loading large
amounts of data at once into RAM, iterate over the results of `load_finapres()` instead of
creating one large `dict`.

The attrs of each Series (e.g. `data['reBAP'].attrs`) will contain the patient and
measurement metadata extracted from the CSV. The Novascope Version and Serial Number are
not yet extracted from the files.

See the [Example Notebook](./Example.ipynb) for an in depth usage example.

We export individual Series as the data has no common time frame. Each signal has their 
own sampling rate and timestamps. If you want to have everything in one DataFrame, there
are two CSVs where Finapres has sampled the data into a single file. However it is
inconvenient to work with, as there are many columns filled with `NaN` when the signal
couldn't be sampled onto the same time frame. Have a look at:

- `Raw Data Export Trend` (coarse time resolution)
- `Raw Data Export Waveform` (finer time resolution)

## Novascope Types
These are the types (`NOVASCOPE_TYPES`) that you can select with a rough description taken
from the manual where possible. There might be more as we might not have bought every
extension module that Finapres provides. If so feel free to open an issue and I will
extend the list:

```python
'Arm': 'Arm(mmHg)', # Arm Cuff pressure during BraCal (NOTE absent from manual)
'beatArtifact': 'beatArtifact()', # Set of possible artifacts than can occur during the recording. It contains the quality of the corresponding beat-to-beat data
'Block': 'Block(-)',
'BRS': 'BRS(ms/mmHg)',
'BSA': 'BSA(m^2)', # Body surface area of patient, estimated from patient data
'CamFlash': 'CamFlash(V)',
'CI': 'CI(l/min/m^2)', # Cardiac Index (= CO/BSA)
'CO': 'CO(l/min)', # Cardiac Output (= SV*HR)
'Cwk': 'Cwk(ml/mmHg)', # Windkessel Compliance: Total Arterial compliance at diastolic pressure (C)
'DIA Arm': 'DIA Arm(mmHg)',
'dPdt': 'dP/dt(mmHg/s)', # Maximal steepness of the current upstroke
'DPTI': 'DPTI(mmHg*s)', # Diastolic Pressure Time Index: Area under the diastolic portion of the arterial pulse (incisura to next timeUpstroke)
'DPTISPTI': 'DPTI/SPTI(%)', # DPTI/SPTI: Ratio is an index of cardiac oxygen supply/demand
'ECG aVF': 'ECG aVF(mV)', # Augmented Vector Foot ECG waveform
'ECG aVL': 'ECG aVL(mV)', # Augmented Vector Left ECG waveform
'ECG aVR': 'ECG aVR(mV)', # Augmented Vector Right ECG waveform
'ECG C1': 'ECG C1(mV)', # Wilson Chest ECG waveform
'ECG I': 'ECG I(mV)', # Einthoven lead I ECG waveform
'ECG II': 'ECG II(mV)', # Einthoven lead II ECG waveform
'ECG III': 'ECG III(mV)', # Einthoven lead III ECG waveform
'fiAP': 'fiAP(mmHg)', # Finger Arterial Pressure
'fiAPLvl': 'fiAPLvl(mmHg)', # ?fiApHCU? Height Corrected Finger Arterial Pressure
'fiDIA': 'fiDIA(mmHg)', # DIAstolic pressure (from BP signal)
'fiMAP': 'fiMAP(mmHg)', # Mean Arterial Pressure (from BP signal)
'fiSYS': 'fiSYS(mmHg)', # SYStolic pressure (from BP signal)
'Hgt': 'Hgt(mmHg)', # Height: Difference between the two sensors on the HCU
'HR': 'HR(bpm)', # Heart rate derived from best signal
'HR AP': 'HR AP(bpm)', # AP Heart rate
'HR Arm': 'HR Arm(bpm)',
'HR ECG': 'HR ECG(bpm)', # Heart rate derived from the ECG waveform
'HR ECG (RR-int)': 'HR ECG (RR-int)(bpm)',
'HR SpO2': 'HR SpO2(bpm)', # Heart rate derived from the SpO₂ waveform
'IBI': 'IBI(ms)', # Inter Beat Interval derived from BP signal
'LVET': 'LVET(ms)', # Left Ventricular Ejection Time
'Markers': 'Label',
'MAP Arm': 'MAP Arm(mmHg)',
'maxAortaArea': 'maxAortaArea(mm2)', # Maximal surface of aorta section based on patient data and flow correction factor
'mFlow': 'mFlow(l/min)', # Reconstructed Flow
'noBeatDetected': 'noBeatDetected(bool)', # No beat detected
'Pacing': 'Pacing(-)', # Indication of the detected pacing pules in time
'PhysioCalActive': 'PhysioCalActive(bool)', # PhysioCal active detected (only for finger pressure)
'physiocalStatus': 'physiocalStatus()', # Status of the Physiocal algorithm
'Pleth': 'Pleth(nA)', # Amplified signal from the cuff photodiode, which is a Plethysmograph signal
'Raw Data Export Trend': None, # TODO
'Raw Data Export Waveform': None, # TODO
'reAoP': 'reAoP(mmHg)',
'reBAP': 'reBAP(mmHg)', # Reconstructed Brachial Artery Pressure
'reDIA': 'reDIA(mmHg)', # Diastolic brachial pressure (based on reBAP)
'RegionMarkers': None,
'reMAP': 'reMAP(mmHg)', # Mean arterial pressure (based on reBAP)
'Resp Rate': 'Resp Rate(resp/min)', # Respiration rate
'Resp Wave': 'Resp Wave(-)', # Respiration waveform derived from chest impedance measurement
'reSYS': 'reSYS(mmHg)', # Systolic brachial pressure (based on reBAP)
'Rp': 'Rp(mmHg.s/ml)', # Peripheral Resistance (R): Parameter of Windkessel model, adapts to changes in mean flow
'RPP': 'RPP(mmHg/min)', # Rate Pressure Product (= SYS*HR)
'RR-int': 'RR-int(ms)', # RR-interval: Time between two successive R peaks in the ECG waveform
'SpO2': 'SpO2(%)', # SpO₂ Value: Hemoglobin Oxygen Saturation Level
'SpO2 Blip': 'SpO2 Blip(-)', # SpO₂ Pulse Strength: Quality indication of the SpO₂ detection
'SpO2 Mod': 'SpO2 Mod(%)', 
'SpO2 Wave': 'SpO2 Wave(-)', # Plethysmograph waveform, non-normalized
'SPTI': 'SPTI(mmHg*s)', # Systolic Pressure Time Index: Area under the systolic portion of the arterial pulse (timeUpstroke to incisura)
'SV': 'SV(ml)', # Stroke Volume
'SVI': 'SVI(ml/m^2)', # Stroke Volume Index (= SV/BSA)
'SYS Arm': 'SYS Arm(mmHg)',
'SVR': 'SVR(mmHg*s/ml)',
'SVRI': 'SVRI(mmHg.s/ml.m^2)',
'TPR': 'TPR(mmHg*s/ml)', # Total Peripheral Resistance (Parameter of Windkessel model, Zao + Rp)
'TPRI': 'TPRI(mmHg.s/ml.m^2)', # Total Peripheral Resistance Index (= TPR/BSA)
'ZAo': 'ZAo(mmHg*s/ml)', # Aortic Impedance: Parameter of Windkessel model, ascending aorta characteristic impedance (Z) at diastolic pressure
# Analog In 1, # Signal from analog input 1 (-10V to 10V)
# Analog In 2, # Signal from analog input 2 (-10V to 10V)
```

---

I am **not** affiliated with [Finapres Medical Systems B.V.](https://www.finapres.com/about-us)
or Demcon in any shape or form. All trademarks mentioned in this repository belong to 
their respective owners. This library is meant as a convenience when working with their
products.
