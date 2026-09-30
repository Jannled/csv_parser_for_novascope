"""
created: 2026-09-08
author: Jannik Schmöle
"""

from collections.abc import Iterable
from pathlib import Path
from statistics import mean
from typing import Any, Literal, NamedTuple, cast

import pandas as pd
from matplotlib.axes import Axes

# Hardware config : ECG, Respiration, SpO2, ArmCuff, AnalogIO, Basic

NOVASCOPE_MEASUREMENT_METADATA = [
	'Measurement', 'Reference', 'Age(yrs)', 'Height(cm)', 'Weight(kg)', 'Gender',
	'FlowCorrection(%)', 'Procedure', 'Application', 'MeasurementStart', 'Patient',
	'Physician'
]

NOVASCOPE_TYPES = Literal[
	'Arm', 'beatArtifact', 'Block', 'BRS', 'BSA', 'CamFlash', 'CI', 'CO', 'Cwk',
	'DIA Arm', 'dPdt', 'DPTI', 'DPTISPTI', 'ECG aVF', 'ECG aVL', 'ECG aVR', 'ECG C1',
	'ECG I', 'ECG II', 'ECG III', 'fiAP', 'fiAPLvl', 'fiDIA', 'fiMAP', 'fiSYS', 'Hgt',
	'HR', 'HR AP', 'HR Arm', 'HR ECG', 'HR ECG (RR-int)', 'HR SpO2', 'IBI', 'LVET',
	'Markers', 'MAP Arm', 'maxAortaArea', 'mFlow', 'noBeatDetected', 'Pacing',
	'PhysioCalActive', 'physiocalStatus', 'Pleth', 'Raw Data Export Trend',
	'Raw Data Export Waveform', 'reAoP', 'reBAP', 'reDIA', 'RegionMarkers', 'reMAP',
	'Resp Rate', 'Resp Wave', 'reSYS', 'Rp', 'RPP', 'RR-int', 'SpO2', 'SpO2 Blip',
	'SpO2 Mod', 'SpO2 Wave', 'SPTI', 'SV', 'SVI', 'SYS Arm', 'SVR', 'SVRI', 'TPR', 'TPRI',
	'ZAo'
]

NOVASCOPE_FILES: dict[NOVASCOPE_TYPES, str|None] = {
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
}


## The header for most files is 7 rows, the exceptions are listed here
NOVASCOPE_HEADER_LEN: dict[NOVASCOPE_TYPES, int] = {
	'Markers': 0
}


class BloodPressure(NamedTuple):
	sys: float # Systolic Blood Pressure
	dia: float # Diastolic Blood Pressure


def load_finapres(folder_path: str|Path, whitelist: list[NOVASCOPE_TYPES]|None=None):
	"""
	:param whitelist: The scope types that should be returned (keys in `FINAPRES_FILES`).
		`None` if all data shall be returned
	"""

	files = sorted(Path(folder_path).glob("*.csv"))

	for file in files:
		if not file.is_file():
			continue

		## e.g. "2026-03-16_10.50.45 DIA Arm.csv"
		_scope_date, scope_type = file.stem.split(maxsplit=1)
		assert scope_type in NOVASCOPE_FILES

		col_name = NOVASCOPE_FILES[scope_type]

		## Skip files that do not contain exactly one data column
		if col_name is None:
			continue

		## If whitelist is enabled, skip over all unwanted files
		if whitelist is not None and scope_type not in whitelist:
			continue
		
		try:
			series = load_finapres_csv(file, scope_type)
		except ValueError:
			## The Markers file of the old Novascope versions e.g 20210222_V1.12.R6333 is different
			series = load_finapres_csv(file, scope_type, old_version=True)

		yield scope_type, series


def load_finapres_csv(file: Path, scope_type: NOVASCOPE_TYPES, old_version: bool = False):
	time_col_name = 'Time' if old_version else 'Time(sec)'
	data_col_name = NOVASCOPE_FILES[scope_type]
	header_len = NOVASCOPE_HEADER_LEN.get(scope_type, 7)
	COL_SEP = ';'

	metadata: dict[str, Any] = {}

	## Most files have a header, for those files without one skip the extraction
	if header_len == 7:
		df_meta = pd.read_csv(
			file, sep=COL_SEP, skiprows=4, nrows=1, skip_blank_lines=True,
			usecols=NOVASCOPE_MEASUREMENT_METADATA
		)
		metadata = cast(dict[str, Any], df_meta.iloc[0].to_dict())

	## Skip over the header to extract the data
	df = pd.read_csv(
		file, sep=COL_SEP, skiprows=header_len, skip_blank_lines=True,
		usecols=[time_col_name, data_col_name]
	)

	## Extract the relevant row
	series = cast(pd.Series, df.set_index(time_col_name)[data_col_name])
	series.index = pd.to_timedelta(series.index, unit="s")

	series.attrs.update(metadata)

	return series


def plot_markers(markers: pd.Series, ax: Axes):
	for time, label in markers.items():
		x = time.total_seconds()

		ax.axvline(
			x=x,
			color='black',
			linestyle='--',
			linewidth=0.8,
			zorder=3
		)

		ax.annotate(
			str(label),
			xy=(x, 1),
			xycoords=('data', 'axes fraction'),
			xytext=(3, -3),
			textcoords='offset points',
			rotation=90,
			va='top',
			ha='left',
			color='black',
			fontsize=9,
			clip_on=False
		)


def marker_arm_cuff_bp(marker: str):
	"""
	Extract the blood pressure from a marker (`{MEASUREMENT_TIME} Markers.csv`). 
	
	:param marker: Valid values look like `ArmCuff: 120/80`. `ArmCuff: Abort` and
		`ArmCuff: Start` will return `None`, all other values throw a `ValueError`.
	"""

	PREFIX = 'ArmCuff:'
	marker = marker.removeprefix(PREFIX).strip()

	if marker.endswith(('Abort', 'Start')):
		return None

	bp = BloodPressure(*( # Spread iterator into Tuple
		float(s.strip()) for s in marker.split('/'))
	)

	assert bp.sys > bp.dia, f'Implausible blood pressure, {bp.sys}/{bp.dia} SYS < DIA'
	return bp


def marker_braCal_bp(marker: str):
	"""
	Extract the average blood pressure that NovaScope uses for brachiales calibration 
	(usually the system does two ArmCuff readings).
	
	:param marker: Something like `BraCal: 122.5/70.5, Δ-38`. `BraCal: begin auto` will 
		return `(None, None)`, all other values throw a `ValueError`.

	TODO No clue what the Δ value means, Clanker has no idea as well.
	Maybe this is the correction applied to the fiAP values to retrieve reBAP?
	"""

	PREFIX = 'BraCal:'
	marker = marker.removeprefix(PREFIX).strip()

	if marker.endswith('begin auto'):
		return None, None

	raw_bp, raw_delta = marker.split(',', maxsplit=1)
	bp = marker_arm_cuff_bp(raw_bp)
	delta = int(raw_delta.lstrip().removeprefix('Δ').strip())

	if bp is None:
		raise ValueError(f'Could not extract blood pressure from "{raw_bp}"')

	return bp, delta


def average_bp(pressures: Iterable[BloodPressure]):
	"""Calculate the average systole/diastole from the given blood pressures."""
	return BloodPressure(*map(mean, zip(*pressures), strict=True))
