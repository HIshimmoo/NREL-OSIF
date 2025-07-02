Open Source Impedance Fitter (OSIF) is a program that allows the user to fit electrochemical impedance spectra of Proton-exchange membrane fuel cells collected under a hydrogen/nitrogen (anode/cathode) environment to an accepted quasi-transmission line model (1), or one dimentional linear diffusion or spherical diffusion models (2).

To use OSIF, the following non-default python packages will have to be downloaded:
  - pandas (uses openpyxl for Excel files)
  - matplotlib
  - numpy
  - scipy

Versions 1.23 and 2.0 now include a helper function ``import_xlsx_file``
to load Excel data outside of the GUI.
  
The default python version the program is written for is 3.x, though it can be used in python 2.x (see in "How to Use OSIF" file in the repository)

The user must have impedance data in one of the following formats (see example data folder in repository):
  - An excel spread sheet with columns as, Index, Frequency (Hz), Z' (Ω), -Z'' (Ω), Z (Ω), -Phase (°), Time (s)
  - A tab delimited text file with a header depicting the columns as Index, Frequency (Hz), Z' (Ω), -Z'' (Ω), Z (Ω), -Phase (°), Time (s) 
  
Where in Z' is the real part of the measured impedance, Z'' is the imaginary part of the measured impedance, and Z is the modulus of the measured impedance.

Starting with version 2.1 the program automatically estimates the membrane
resistance (Rmem) from the loaded data.  The value of Z' at which Z'' crosses
zero in the Nyquist plot is used as the estimate.  During fitting Rmem is
constrained to vary by at most ±10 % from this estimate.
  
  
For instructions on how to, install python on a windows or mac platform (in order to use OSIF) and running OSIF as well as more information on how OSIF works see the "How to Use OSIF" file in the repository.



(1) Setzler, B. P., & Fuller, T. F. (2015). A Physics-Based Impedance Model of Proton Exchange Membrane Fuel Cells Exhibiting Low-Frequency Inductive Loops. Journal of The Electrochemical Society, 162(6), F519-F530. doi:10.1149/2.0361506jes
(2) Jean-Paul Diard (BioLogic), Bernard Le Gorrec (UJFG-INPG), C Montella. Handbook of Electrochemical Impedance Spectroscopy. DIFFUSION IMPEDANCES.
https://www.researchgate.net/publication/342833389_Handbook_of_Electrochemical_Impedance_Spectroscopy_DIFFUSION_IMPEDANCES
