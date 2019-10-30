# wb_sanity
Python wrapper for everyday visualization with [Connectome Workbench](https://www.humanconnectome.org/software/connectome-workbench)

This is a simple Python interface to performing standard every day visualization tasks in Connectome Workbench. You might have an atlas or a set or regions of interest that you just want to display on the surface, and maybe attach some values to each region (e.g., a weighting, a connectivity metric, a principal component loading). Or, you might want to project data in MNI coordinates onto a surface\*. Unfortunately, these simple tasks are not immediately obvious when using Connectome Workbench, which can be overwhelming for users. 

Python was selected because of its quality neuroimaging/fMRI ecosystem that is continually growing. Therefore, this package makes it easy to integrate Connectome Workbench utilites into your Python neuroimaging projects. `wb_command` gets called under the hood, and `wb_sanity` makes it convenient to make or manipulate your `cifti` files, readying them for visualization. To actually display the visualizations, you'll need to use Connectome Workbench's `wb_viewer` itself. 

## What's in a name?

`wb_sanity` is a tongue-and-cheek name that pokes fun at Connectome Workbench's powerful-yet-overwhelming nature (the name is inspired by [arxiv-sanity](http://www.arxiv-sanity.com/)). I should emphasize that Connectome Workbench is a *great* tool and serves its purpose very well, and the developers did a great job at building a real powerhouse. However, in my opinion, 1) it has a steep learning curve; and 2) the documentation, while excellent and thorough at describing its functions and their parameters, is sparse when it comes to simple use-cases and tutorials\*\* (i.e. you just want to use it as a basic visualization tool). I'm hoping that this will improve over time, and maybe this package can serve as a gateway and encourage people to use Connectome Workbench in its full capacity in their analyses.

## Alternatives

If you're looking for surface visualization/analysis packages and don't necessarily require Connectome Workbench, there are other great options available in the Python ecosystem. These alternatives include [Pysurfer](https://pysurfer.github.io/), [Nilearn's surface plotting utilities](https://nilearn.github.io/plotting/index.html#surface-plotting), and [Pycortex](https://gallantlab.github.io/index.html). I highly recommend checking them out!

# Installation 

**Step 1:** Install Connectome Workbench, which can be done here: https://www.humanconnectome.org/software/get-connectome-workbench  

**Step 2:** Install wb_sanity. 

1. Clone this repository to a local directory:
```
git clone git@github.com:danjgale/wb_sanity.git
```

2. Then `cd` into the directory and pip install:

```
cd wb_sanity
pip install -e .
``` 

## Links

- [Connectome Workbench](https://www.humanconnectome.org/software/connectome-workbench)
- [Connectome Workbench Tutorial v1.0](https://www.humanconnectome.org/storage/app/media/documentation/tutorials/Connectome_WB_Tutorial_v1.0.pdf)
- [Connectome Workbench Github](https://github.com/Washington-University/workbench)

---
**\*** I'm aware that some call this a 'faux-pas' and actively discourage it (i.e. you should be doing all your analyses on the surface from the start, and projecting data from volume-space to surfaces introduces some inaccuracies). However, volume-based analysis is still very much ubiquitous; it is the dominant approach right now. So, projecting from volume to surface is extremely common and accepted by many. So, this is a disclaimer in the sense that if you want to be as accurate as possible, you should follow the recommendations of the people behind Connectome Workbench. If you want to do what many people consider as 'plenty good enough', proceed with caution!

**\*\*** Some great tutorials out there include ones by [Jo Etzel](https://mvpa.blogspot.com/2017/08/getting-started-with-connectome.html)