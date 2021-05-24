# A Simple Framework For Solving Optimization Problems in Python  [![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Tutorial%3A%20A%20Simple%20Framework%20For%20Solving%20Optimization%20Problems%20in%20Python&url=https://github.com/ekhoda/optimization-tutorial&via=EhsanKhoda&hashtags=python,orms,programming,optimization)
The framework is shown using a simple production planning example. 
The optimization model is written in `pulp` and the use of 5 different solvers is shown: 
CBC (default), Gurobi, CPLEX, XPRESS, and GLPK.
For reference, the optimization model is also written and solved with `gurobipy`, `docplex`, and `xpress`.

## Modules
All the modules that start with `execute` can be run as the main module. 
The optimization problem is modeled using `pulp`, `gurobipy`, `docplex`, and `xpress` packages. 
The codes are written for two different approaches: 1) scripting and 2) a more modular and object-oriented approach. 

### Scripting
You can start your journey of learning `pulp`, `gurobipy`, `docplex` or `xpress` 
using `execute_pulp.py`, `execute_grb.py`, `execute_docplex.py`, and `execute_xpress.py` scripts, respectively. 
There is documentation in each of these modules to learn different ways of defining variables and constraints.

### Object-Oriented Approach
`execute_oo.py` is the starting module of this approach. Depending on what you like to learn, 
check `optimization_model_pulp.py`, `optimization_model.grb.py`, 
`optimization_model_docplex.py` or `optimization_model_xpress.py`. 
Due to similarities between these modules and what was described in the 
`execute_pulp.py`, `execute_grb.py`, `execute_docplex.py` and `execute_xpress.py`, 
some of the documentation are omitted.
The default values in `parameters.py` are set to run the model in `pulp` 
which is also what you should expect by running `execute_oo.py`. 
If you wish `execute_oo.py` to run the model with CPLEX, Gurobi, or XPRESS, 
the least you should do is to change the value of `module` to `'cplex'`, `'gurobi'`, 
or `'xpress'`, respectively, in the `parameters.py`.

Regardless of the approach, we use the functionalities defined in `helper.py`, `process_data.py`, and `parameters.py` modules.

Note that compared to the standalone `execute_*.py` modules, 
the `optimization_model_*.py` modules have more details in their `optimize` function 
that show handling of various parameters. Moreover, `optimization_model_docplex.py` shows 
how to solve the model, using the local installation of CPLEX or with DOcplexcloud.

## Production Planning Example
We are responsible for scheduling the monthly production plan of a product for a year. Here are the assumptions:
- The demand of the product, unit production cost, and production capacity in each month are known and can be found [here](data/csv/input_data.csv).
- Inventory holding cost occurs at the end of each month.
- Holding cost is $8 per unit per month.
- There are 500 units of inventory available at the beginning of the first month. Unit holding cost and initial inventory are stored [here](data/csv/parameters.csv).
- No shortage is allowed.

The data for this example are stored in both *csv* and *excel* formats and you can use either by specifying your choice in the `parameters.py`. The output results are shown in the [output folder](output).

### Problem Formulation
**Parameters:**  
*h* : unit holding cost  
*p* : production capacity per month  
*I<sub>0</sub>* : initial_inventory  
*c<sub>t</sub>* : unit production cost in month *t*  
*d<sub>t</sub>* : demand of month *t*  

**Variables:**  
*X<sub>t</sub>* : Amount produced in month *t*  
*I<sub>t</sub>* : Inventory at the end of period *t*  

**Model**  

<img src="https://latex.codecogs.com/svg.latex?\min&space;\sum_{t\in&space;T}hI_{t}&space;&plus;&space;c_{t}X_{t}\\&space;s.t:\\&space;I_{t-1}&space;&plus;&space;X_{t}&space;-&space;d_{t}&space;=&space;I_{t}&space;\;\;\;\;&space;\forall&space;t\in&space;T&space;\\&space;X_{t}&space;\leq&space;p&space;\;\;\;\;&space;\forall&space;t\in&space;T&space;\\&space;X_{t},&space;I_{t}&space;\geq&space;0&space;\;\;\;\;&space;\forall&space;t\in&space;T&space;\\" title="\min \sum_{t\in T}hI_{t} + c_{t}X_{t}\\ s.t:\\ I_{t-1} + X_{t} - d_{t} = I_{t} \;\;\;\; \forall t\in T \\ X_{t} \leq p \;\;\;\; \forall t\in T \\ X_{t}, I_{t} \geq 0 \;\;\;\; \forall t\in T \\" />

## Extra
You can check [this blog](https://ehsankhoda.medium.com/tutorial-a-simple-framework-for-optimization-programming-in-python-using-pulp-and-gurobi-1e73e76532f2) that 
gives some backstory about the framework and more details about different modules.
