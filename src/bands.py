import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from ase.io import write, Trajectory, read
from gpaw import GPAW, FermiDirac
from gpaw.unfold import Unfold, find_K_from_k
import tabulate
import pandas as pd 
import os 
import glob as glob
from IPython.display import HTML
from utils import create_dir


class Bands:
    def __init__(self,path_to_files,diroutput='json'):
        
        self.path_to_files = path_to_files
        
        if os.path.exists(self.path_to_files):
            print(f"{self.path_to_files} it's ok")
        else:
            raise FileNotFoundError(f'The {path_to_files} does not exist')
        
        self.abspath_to_files = os.path.abspath(path_to_files)
        self.bs               = None
        self.xcoords          = None
        self.ekn_array        = None
        self.ch_file          = None
        self.fermi_level      = None
        self.dos              = None
        self.dos_array        = None
        self.diroutput        = diroutput
        self.files            = sorted(glob.glob(self.abspath_to_files+'/*.gpw'))
        self._df_files        = pd.DataFrame(self.files,columns=['gpw File'])
        self.files_to_dframe  = [f.split('/')[-1] for f in self.files]
        self.df_to_display    = pd.DataFrame(self.files_to_dframe,columns=['gpw File'])
        self.spin_up          = 0
        self.spin_down        = 1
        display(self.df_to_display)
    
    
    def get_bands(self,nofile:int,**kwargs) -> None:
        """function to get band structure from specfic gpw file, this function returns an array"""
        
        # if nofile not in self.df_files['File'].iloc[nofile]:
        #     raise IndexError("Does not input number file")
        
        def pretty(kpt):
            if kpt == 'G':
                kpt = r'$\Gamma$'
            elif len(kpt) == 2:
                kpt = kpt[0] + '$_' + kpt[1] + '$'
            return kpt
        
        self.ch_file     = self._df_files['gpw File'].iloc[nofile] 
        print(f'You chose {self.files_to_dframe[nofile]}')   
        
        # get bands parameters 
        _calc_bands      = GPAW(self.ch_file)
        self.bs          = _calc_bands.band_structure()
        self.fermi_level = _calc_bands.get_fermi_level()
        no_of_spins      = _calc_bands.get_number_of_spins()
        energies         = self.bs.energies-self.fermi_level
        no_of_bands      = _calc_bands.get_number_of_bands()        
        #from gpaw documentation.
        self.xcoords, label_xcoords, x_labels = self.bs.get_labels()
        e_range          = len(self.xcoords)
        self.ekn_array = np.zeros(( no_of_spins,len(self.xcoords),no_of_bands))

        x_labels = [i if 'K' not in i else "K" for i in x_labels ]
        x_labelsk = [pretty(i) for i in x_labels]
        
        self.ekn_array[:,:,0]=self.xcoords
        for spin, e_kn in enumerate(energies):
            for col,e_k in enumerate(e_kn.T[1:]):
                self.ekn_array[spin,:,col+1] = e_k
        
        # export dos    
        e_up, self.dos_up   = _calc_bands.get_dos(spin=self.spin_up,**kwargs)
        e_down, self.dos_down = _calc_bands.get_dos(spin=self.spin_down,**kwargs)
        
        self.dos_array = np.zeros((no_of_spins,len(e_up),2))
        self.dos_array[0,:,0] = e_up-self.fermi_level
        self.dos_array[0,:,1] = self.dos_up 
        self.dos_array[1,:,0] = e_down-self.fermi_level
        self.dos_array[1,:,1] = -self.dos_down
        
        
        results: Dict[str, Any] = {'energies'     : self.ekn_array.tolist(),
                                   'xcoords'      : self.xcoords.tolist(),
                                   'label_xcoords': label_xcoords.tolist(),
                                   'x_labels'     : x_labels,
                                   'energies_dim' : self.ekn_array.shape,
                                   'dos'          : self.dos_array.tolist()
                                   }      

        #export output to json file
        from utils.outfiles import calc2json
        try:
            calc2json(results,self.files_to_dframe[nofile])
        except ValueError:
            print(f"Can't created {self.ch_file}!")
            
  
        return results
    


    @property
    def get_dframe(self):
        # Return dataframe with gpw files in terminal
        return self._df_files

     
    # def __repr__(self):
    #     return ('{} energies=[{} values], reference={})'
    #             .format(self.__class__.__name__, self.path,
    #                     '{}x{}x{}'.format(*self.energies.shape),
    #                     self.reference))

    

    

        
        
        
        
        
        
        























































