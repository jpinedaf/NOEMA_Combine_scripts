Generate uv-tables
==================

The process of generating uv-tables is a crucial step in the NOEMA_Combine package,
as it prepares the interferometric data for further analysis and combination with single-dish data.

The uv-tables are created using a dedicated script that automates the extraction and formatting of the data.
To generate these scripts, you can use the following command:

.. code-block:: python

    from noema_combine import generate_uvt
    setup_name = "your_setup_name"
    config_path = "path/to/your/config/file.yml"
    generate_uvt.process_source(setup_name, config_path)  
    
where the ``setup_name`` corresponds to the specific observational setup you are working with, and ``config_path`` is the path to your configuration file that contains the necessary parameters for the uv-table generation.
This is an example of the configuration file structure:

.. code-block:: yaml

  receiver : 3
  highres_parameters: # for LO LI UI UO quarters
    number_windows: 38 # number of high-resolution windows
    LI_start: 23   # starting window for LI quarter (1-indexed)
    UI_start: 32   # starting window for UI quarter (1-indexed)
    UO_start: 40   # starting window for UO quarter (1-indexed)
  setups:
    setup001:
      sources:
        - Per-emb-2
        - L1448-IRS3B
      C-files:
        - file: ../hpbs/Cconfig/hpb-001-04-dec/04-dec-2019-l19mb001
      D-files:
        - file: ../hpbs/Dconfig/hpb-001-05-sep/05-sep-2020-l19mb001
        - file: ../hpbs/Dconfig/hpb-001-06-aug/06-aug-2020-l19mb001
            - RF calibration type: baseline
        - file: ../hpbs/Dconfig/hpb-001-05-apr/05-apr-2021-l19mb001
            - phase calibration type: baseline
        - file: ../hpbs/Dconfig/hpb-001-08-apr/08-apr-2021-l19mb001
            - amplitude calibration type: baseline

the files above are the `hpb` files (usually generated with the NOEMA pipeline), and they will be used within `CLIC` to generate the uv-table comprising of all the observations for the specified sources.

The different sections of the configuration file are described below:

- **receiver**: Specifies the receiver band used for the observations (e.g., 1 for 3mm, and 3 for 1mm).
- **highres_parameters**: Contains parameters related to high-resolution spectral windows, including the number of windows and the starting indices for each quarter (LI, UI, UO). Notice that the broadband windows go from 1 to 8. first window is 
    - **LI_start, UI_start, UO_start**: The starting indices for the LI, UI, and UO quarters, respectively. These parameters are essential for accurately generating uv-tables that reflect the observational setup and data characteristics.
- **setups**: This section lists the observational setups, including the sources observed and the corresponding C and D configuration files used for calibration.
    - **sources**: A list of source names included in the setup.
    - **C-files**: A list of calibration files for the C configuration.
        - **file**: The path to the calibration file.
    - **D-files**: A list of calibration files for the D configuration.
        - **file**: The path to the calibration file.
            - **RF calibration type**: (optional) Specifies the calibration type for RF calibration. The default calibration type is `antenna`, but you can specify different calibration types for RF, phase, and amplitude calibrations as needed (only baseline is supported at the moment).
            - **phase calibration type**: (optional) Specifies the calibration type for phase calibration.
            - **amplitude calibration type**: (optional) Specifies the calibration type for amplitude calibration.
         

The code will generate scripts for the different combinations of the NOEMA array configurations. 
Then, the user needs to run the generated scripts within the `CLIC` environment to produce the uv-tables.