"""Independent scientific and interaction checks for the two learning notebooks."""
from pathlib import Path
import argparse
import ast
import json
import contextlib
import io
import itertools
import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir())/"klimov-lesson-mpl"))
import nbformat
import numpy as np
from scipy import constants
from scipy.integrate import quad
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
FILES=["01_foundations.ipynb","02_spherical_quantum_box.ipynb"]

def independent_physics(ns):
    ns["model_checks"]()
    # Compare to a direct SI evaluation independent of the notebook's unit helper.
    hbar=constants.hbar
    for R in [1.5,3.,7.]:
        si=hbar*hbar*np.pi**2/(2*.13*constants.m_e*(R*1e-9)**2)/constants.e
        assert np.isclose(ns["energy"](1,0,R,.13),si,rtol=1e-12)
    # Analytic ground-state radial CDF versus quadrature.
    for a,b in [(0,.1),(.4,.6),(.9,1)]:
        exact=(b-a)-(np.sin(2*np.pi*b)-np.sin(2*np.pi*a))/(2*np.pi)
        numeric=quad(lambda s:ns["radial_prob"](s),a,b,epsabs=1e-12)[0]
        assert np.isclose(numeric,exact,atol=1e-12)
    # Separate quadrature of the 2D shell-averaged Coulomb integral.
    p=lambda s:2*np.sin(np.pi*s)**2
    numeric=quad(lambda s:2*p(s)*quad(lambda t:p(t),0,s)[0]/s,0,1)[0]
    assert np.isclose(numeric,ns["coulomb_coefficient"](),atol=1e-10)
    # Orthogonality beyond the first pair and positive, correctly sorted levels.
    for ell in range(3):
        for n in range(1,4):
            integral=quad(lambda s:s*s*ns["radial"](s,n,ell)**2,0,1)[0]
            assert np.isclose(integral,1,atol=1e-9)
            for m in range(1,n):
                overlap=quad(lambda s:s*s*ns["radial"](s,n,ell)*ns["radial"](s,m,ell),0,1)[0]
                assert abs(overlap)<1e-9
    roots=[ns["root"](*v) for v in ns["STATES"].values()]
    assert np.all(np.diff(roots)>0)
    terms=ns["pair_terms"](3)
    assert np.isclose(terms[-1],1.9837,atol=1e-4)
    assert np.isclose(ns["pair_terms"](3,eps=12)[2],terms[2]/2)
    assert np.isfinite(ns["radial"](0,1,0))
    assert ns["radial"](0,1,0)>0

def interaction_checks(ns):
    count=0
    for key,(fn,controls,out) in ns["LABS"].items():
        defaults={k:w.value for k,w in controls.items()}
        trials=[]
        # Every discrete option; every slider endpoint; combined numeric extremes.
        for name,w in controls.items():
            if hasattr(w,"options"):
                values=[v[1] if isinstance(v,tuple) else v for v in w.options]
            elif isinstance(w.value,bool): values=[False,True]
            elif isinstance(w.value,tuple): values=[(w.min,w.min),(w.min,w.max),(w.max,w.max)]
            else: values=[w.min,w.max]
            for value in values: trials.append((name,value))
        for name,value in trials:
            with capture_output() as captured:
                controls[name].value=value   # invoke the registered observer
                fn(**{k:w.value for k,w in controls.items()}) # also surface any exception directly
                controls[name].value=defaults[name]
            assert "Traceback" not in captured.stdout+captured.stderr,(key,captured)
            assert not any(o.get("output_type")=="error" for o in out.outputs),key
            plt.close("all")
            count+=1
        for extreme in ["min","max"]:
            args=defaults.copy()
            for name,w in controls.items():
                if hasattr(w,extreme) and not isinstance(w.value,tuple):
                    args[name]=getattr(w,extreme)
            with capture_output(): fn(**args)
            plt.close("all")
    for key,(select,button,result,check,correct,explanations) in ns["QUIZZES"].items():
        select.value=-1;button.click()
        assert "Choose an answer" in result.value
        for i in range(len(explanations)):
            select.value=i;button.click()
            assert explanations[i] in result.value
            assert ("Correct." in result.value)==(i==correct)
        select.value=-1
    return count


def foundations_checks(ns):
    # Derive normalization and orthogonality independently of the plotting functions.
    for a in [1.,3.,6.]:
        for n in range(1,5):
            psi=lambda x:np.sqrt(2/a)*np.sin(n*np.pi*x/a)
            assert np.isclose(quad(lambda x:psi(x)**2,0,a)[0],1,atol=1e-12)
            assert abs(psi(0))+abs(psi(a))<1e-12
            for m in range(1,n):
                overlap=quad(lambda x:psi(x)*np.sqrt(2/a)*np.sin(m*np.pi*x/a),0,a)[0]
                assert abs(overlap)<1e-12
            # A finite-difference derivative verifies the Schrödinger residual.
            x=np.linspace(.05*a,.95*a,101);dx=1e-4*a
            curvature=(psi(x+dx)-2*psi(x)+psi(x-dx))/dx**2
            exact=-(n*np.pi/a)**2*psi(x)
            assert np.allclose(curvature,exact,rtol=2e-6,atol=1e-6)
    assert abs(np.sin(1.5*np.pi))>.99
    assert abs(np.sin(2*np.pi))<1e-12
    assert np.isclose(quad(lambda x:(2*np.sqrt(2/3)*np.sin(np.pi*x/3))**2,0,3)[0],4)

def native_form_checks(nb,shell):
    """Exercise the Colab code path without depending on Google's runtime."""
    ns=shell.user_ns
    ns["IN_COLAB"]=True
    original_display=ns["display"]
    displayed=[]
    ns["display"]=lambda *items:displayed.extend(getattr(item,"data","") for item in items)
    count=0
    try:
        for cell in nb.cells:
            if cell.cell_type!="code" or "# @param" not in cell.source:
                continue
            assert '{run: "auto", single-column: true}' in cell.source
            with capture_output() as captured:
                result=shell.run_cell(cell.source)
            assert result.error_in_exec is None,result.error_in_exec
            assert "Traceback" not in captured.stdout+captured.stderr
            tree=ast.parse(cell.source)
            calls=[n.value for n in tree.body if isinstance(n,ast.Expr)
                   and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name)
                   and n.value.func.id in ["lab","quiz"]]
            call=calls[-1]
            if call.func.id=="lab":
                fields=next(k.value for k in call.keywords if k.arg=="form_values")
                expected=eval(compile(ast.Expression(fields),"<fields>","eval"),ns)
                key=ast.literal_eval(call.args[0])
                assert {k:w.value for k,w in ns["LABS"][key][1].items()}==expected
                # Emulate editing a native slider and rerunning the whole cell.
                for line in cell.source.splitlines():
                    if '# @param {"type": "slider"' not in line:continue
                    before,annotation=line.split("# @param",1)
                    config=json.loads(annotation)
                    variable=before.split("=")[0].strip()
                    changed=cell.source.replace(line,variable+" = "+repr(config["max"])+" # @param"+annotation)
                    with capture_output() as captured:
                        result=shell.run_cell(changed)
                    assert result.error_in_exec is None,result.error_in_exec
                    expected=eval(compile(ast.Expression(fields),"<fields>","eval"),ns)
                    assert {k:w.value for k,w in ns["LABS"][key][1].items()}==expected
                    break
            else:
                choices=ast.literal_eval(call.args[2]);correct=ast.literal_eval(call.args[3])
                for i,choice in enumerate(choices):
                    changed=cell.source.replace('your_answer = "Choose an answer"', 'your_answer = '+repr(choice))
                    displayed.clear()
                    with capture_output() as captured:
                        result=shell.run_cell(changed)
                    assert result.error_in_exec is None,result.error_in_exec
                    html=" ".join(x for x in displayed if isinstance(x,str))
                    assert ("Correct." in html)==(i==correct),html
            plt.close("all")
            count+=1
    finally:
        ns["IN_COLAB"]=False
        ns["display"]=original_display
    return count


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--output-dir",type=Path)
    args=parser.parse_args()
    outdir=args.output_dir or Path(tempfile.mkdtemp(prefix="klimov-review-"))
    outdir.mkdir(parents=True,exist_ok=True)
    for file in FILES:
        nb=nbformat.read(ROOT/file,as_version=4)
        nbformat.validate(nb)
        shell=InteractiveShell()
        ns=shell.user_ns
        for i,cell in enumerate(nb.cells):
            if cell.cell_type=="code":
                with capture_output() as captured:
                    # The non-kernel smoke pass uses Agg. Fresh-kernel execution below
                    # runs the original inline-backend instruction unchanged.
                    source=cell.source.replace("get_ipython().run_line_magic('matplotlib', 'inline')", "pass")
                    result=shell.run_cell(source)
                assert result.error_before_exec is None,(file,i,result.error_before_exec)
                assert result.error_in_exec is None,(file,i,result.error_in_exec)
                assert "Traceback" not in captured.stderr+captured.stdout,(file,i,captured)
        if file.startswith("02"):
            independent_physics(ns)
        else:
            foundations_checks(ns)
        count=interaction_checks(ns)
        # Export actual reference plots for visual inspection.
        for key,(fn,controls,_) in ns["LABS"].items():
            original=plt.show
            plt.show=lambda *a,**k:None
            try:
                with capture_output():
                    fn(**{k:w.value for k,w in controls.items()})
                fig=plt.gcf()
                fig.savefig(outdir/f"{file[:2]}-{key}.png",dpi=130,bbox_inches="tight")
            finally:
                plt.show=original
                plt.close("all")
        form_count=native_form_checks(nb,shell)
        print(f"{file}: structure, scientific checks, {count} control changes, {form_count} native forms, and quiz feedback passed.")
        if args.execute:
            from nbclient import NotebookClient
            client=NotebookClient(nb,timeout=180,kernel_name="python3",
                resources={"metadata":{"path":str(ROOT)}})
            client.execute()
            # Ensure errors hidden in widget Output models are checked too.
            state=nb.metadata.get("widgets",{}).get("application/vnd.jupyter.widget-state+json",{}).get("state",{})
            for item in state.values():
                for o in item.get("state",{}).get("outputs",[]):
                    assert o.get("output_type")!="error",(file,o)
            nbformat.validate(nb)
            nbformat.write(nb,outdir/file)
            print(f"{file}: fresh-kernel execution passed; saved in {outdir}.")
    print("All checks passed.")

if __name__=="__main__":
    main()
