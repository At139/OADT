# lookup_tables.py
import sys
import os

# Add gmid to the path for module imports
sys.path.append(os.path.abspath("gmid"))

from mosplot import LookupTableGenerator  # Adjusted import path

def remove_spaces_from_paths(paths):
        """Helper function to remove spaces from each path in a list."""
        return [path.replace(" ", "") for path in paths]

def generate_lookup_table(simulator, model_paths, raw_spice, model_names, vsb, vgs, vds, width, lengths, lookup_table_file):
    model_paths = remove_spaces_from_paths(model_paths)
    
    if (len(raw_spice) == 0):

        obj = LookupTableGenerator(
            description=f"{simulator} simulation",
            simulator=simulator,
            model_paths=model_paths,
            model_names=model_names,
            vsb=vsb,  # Bulk-source voltage sweep
            vgs=vgs,  # Gate-source voltage sweep
            vds=vds,  # Drain-source voltage sweep
            width=width,
            lengths=lengths
        )
    else :
         obj = LookupTableGenerator(
            description=f"{simulator} simulation",
            simulator=simulator,
            model_paths=model_paths,
            raw_spice=raw_spice,
            model_names=model_names,
            vsb=vsb,  # Bulk-source voltage sweep
            vgs=vgs,  # Gate-source voltage sweep
            vds=vds,  # Drain-source voltage sweep
            width=width,
            lengths=lengths
        )
         

    # Build and save the lookup table
    output_file = lookup_table_file
    obj.build(output_file)
    
    return output_file  # Return the location of the saved file
