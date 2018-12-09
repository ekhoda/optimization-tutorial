# A Simple Framework For Solving Optimization Problems in Python  [![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Tutorial%3A%20A%20Simple%20Framework%20For%20Solving%20Optimization%20Problems%20in%20Python&url=https://github.com/ekhoda/optimization-tutorial&via=EhsanKhoda&hashtags=python,orms,programming,optimization)
The framework is shown using a simple production planning example. The optimization model is written in `pulp` and the use of 4 different solvers is shown: CBC (default), Gurobi, CPLEX, and GLPK.
For reference, the optimization model is also written and solved with `gurobipy`.

## Modules
All the modules that start with `execute` can be run as the main module. The optimization problem is modeled using `pulp` or `gurobipy` packages. The codes are written for two different approaches: 1) scripting and 2) a more modular and object-oriented approach. 

### Scripting
You can start your journey of learning `pulp` or `gurobipy` using `execute_pulp.py` and `execute_grb.py` scripts. There is documentation in each of these modules to learn different ways of defining variables and constraints.

### Object-Oriented Approach
`execute_oo.py` is the starting module of this approach. Depending on what you like to learn, check `optimization_model_pulp.py` or `optimization_model.grb.py`. Due to similarities between these two modules and what was described in the `execute_pulp.py` and `execute_grb.py`, some of the documentation are eliminated.

Regardless of the approach, we use the functionalities defined in `helper.py`, `process_data.py`, and `parameters.py` modules.

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

<a href="https://www.codecogs.com/eqnedit.php?latex=\min&space;\sum_{t\in&space;T}hI_{t}&space;&plus;&space;c_{t}X_{t}\\&space;s.t:\\&space;I_{t-1}&space;&plus;&space;X_{t}&space;-&space;d_{t}&space;=&space;I_{t}&space;\hspace{20}&space;\forall&space;t\in&space;T&space;\\&space;X_{t}&space;\leq&space;p&space;\hspace{80}&space;\forall&space;t\in&space;T&space;\\&space;X_{t},&space;I_{t}&space;\geq&space;0&space;\hspace{65}&space;\forall&space;t\in&space;T&space;\\" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\min&space;\sum_{t\in&space;T}hI_{t}&space;&plus;&space;c_{t}X_{t}\\&space;s.t:\\&space;I_{t-1}&space;&plus;&space;X_{t}&space;-&space;d_{t}&space;=&space;I_{t}&space;\hspace{20}&space;\forall&space;t\in&space;T&space;\\&space;X_{t}&space;\leq&space;p&space;\hspace{80}&space;\forall&space;t\in&space;T&space;\\&space;X_{t},&space;I_{t}&space;\geq&space;0&space;\hspace{65}&space;\forall&space;t\in&space;T&space;\\" title="\min \sum_{t\in T}hI_{t} + c_{t}X_{t}\\ s.t:\\ I_{t-1} + X_{t} - d_{t} = I_{t} \hspace{20} \forall t\in T \\ X_{t} \leq p \hspace{80} \forall t\in T \\ X_{t}, I_{t} \geq 0 \hspace{65} \forall t\in T \\" /></a>


## Extra
You can check [this blog](https://medium.com/@ehsankhoda/tutorial-a-simple-framework-for-optimization-programming-in-python-using-pulp-and-gurobi-1e73e76532f2) that gives some backstory about the framework and more details about different modules.
