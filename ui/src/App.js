import './App.css';
import React,{useEffect,useState,Component} from 'react';
import {Text as TextRN} from 'react-native';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import Checkbox from '@mui/material/Checkbox';
import {styled} from '@mui/material/styles';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import TableContainer from '@mui/material/TableContainer';
import LinearProgress, { LinearProgressProps } from '@mui/material/LinearProgress';
import TableRow from '@mui/material/TableRow';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import SubdirectoryArrowRightIcon from '@mui/icons-material/SubdirectoryArrowRight';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import Plot from 'react-plotly.js';

const pyserver = "http://localhost:5555/";

const StyledTableRow = styled(TableRow)(({theme}) => ({'&:nth-of-type(4n-1)':{backgroundColor:theme.palette.action.hover}}));
const UnpaddedTableCell = styled(TableCell)(({theme}) => ({'borderBottom':"none","padding":"0px"}));
class Text extends Component
{
    render() {return (<TextRN style={[{whiteSpace:"unset"},this.props.style]}>{this.props.children}</TextRN>)};
}

function TripleFilter(props)
{
    const {set,val,name,...other} = props;
    return (<TableRow hover onClick={()=>{set(!val);}}>
                <TableCell style={{padding:"0px"}}>
                    <Checkbox checked={val}/>
                </TableCell>
                <TableCell style={{padding:"0px"}}>
                    <Text>
                        <b>{name}</b>
                    </Text>
                </TableCell>
            </TableRow>);
}

function PaperFilter(props)
{
    const {set,val,pmid,title,...other} = props;
    return (<TableCell hover onClick={()=>{set(!val);}}>
                <Table>
                    <TableBody>
                        <TableRow>
                            <UnpaddedTableCell>
                                <Checkbox checked={val}/>
                            </UnpaddedTableCell>
                            <UnpaddedTableCell>
                                <a href={"https://pubmed.ncbi.nlm.nih.gov/"+pmid} target="_blank">
                                    <Text>{[...title].reduce((prev,curr,i)=>(i>50?prev:(prev+curr)),"")+"..."}</Text>
                                </a>
                            </UnpaddedTableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableCell>);
}

function CitationsFilter(props)
{
    const {num,setexp,exp,...other} = props;
    const [open,setopen] = React.useState(false);
    return (<TableCell hover onClick={()=>{;}} style={{"border-width":"0px 0px 0px 1px","border-style":"solid","border-color":"lightgray"}}>
                <Table>
                    <TableBody>
                        <TableRow>
                            <TableCell style={{"border-width":"0px 0px 0px 0px"}}>
                                <Text><center>Cited by {num} papers</center></Text>
                            </TableCell>
                            <TableCell style={{"border-width":"0px 0px 0px 0px"}}>
                                <IconButton aria-label="expand row" size="small" onClick={()=>{setexp(false,!exp);}}>
                                    Search Papers {exp ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                                </IconButton>
                            </TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableCell>);
}

function TripleElement(props)
{
    const {filtset,filtval,entname,fullstring,pad,...other} = props;
    return (<TableCell style={{borderBottom:"none",padding:(pad ? 5 : 0)}}>
                <Table>
                    <TableBody>
                        <TripleFilter set={filtset} val={filtval} name={entname} ty="element" />
                        <TableRow>
                            <TableCell colSpan={2} style={{borderBottom:"none",padding:5}}><Text><center>{fullstring}</center></Text></TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableCell>);
}

function EntityType(props)
{
    const {setfilts,filts,num,tyname,...other} = props;
    return (<TableRow hover onClick={(event) => {setfilts(filts.map((bl,j)=>(num==j?!bl:bl)));}}>
                <UnpaddedTableCell>
                    <Table>
                        <TableBody>
                            <TableRow>
                                <UnpaddedTableCell>
                                    <Checkbox checked={filts[num]}/>
                                </UnpaddedTableCell>
                                <UnpaddedTableCell>
                                    <Text>
                                        <i>{[...tyname].reduce((prev,curr)=>(prev+((curr===curr.toUpperCase())?" "+curr:curr)),"")}</i>
                                    </Text>
                                </UnpaddedTableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </UnpaddedTableCell>
            </TableRow>);
}

function EntityFilters(props)
{
    const {labels,setfilts,filts,...other} = props;
    return (<UnpaddedTableCell>
                <Table>
                    <TableBody>
                         {labels.map((label,i)=>(<EntityType key={i} setfilts={setfilts} filts={filts} num={i} tyname={label} />))}
                    </TableBody>
                </Table>
            </UnpaddedTableCell>);
}

function Row(props)
{
    const {row,...other} = props;
    const [open,setOpen] = React.useState(false);
    const [paperopen,setpaperopen] = React.useState(false);
    const [newrow,setnewrow] = React.useState([]);
    const [sfilt,setsfilt] = React.useState(false);
    const [pfilt,setpfilt] = React.useState(false);
    const [ofilt,setofilt] = React.useState(false);
    const [pmidfilt,setpmidfilt] = React.useState(false);
    const [stypefilts,setstypefilts] = React.useState(row["labels(n)"].map((ty)=>(false)));
    const [otypefilts,setotypefilts] = React.useState(row["labels(m)"].map((ty)=>(false)));
    function setexpand(exp,papers)
    {
        setOpen(exp);
        setpaperopen(papers);
    }
    function filterstr()
    {
        let s = "";
        if(sfilt)
            s += "s="+row.n.Name+"&";
        if(pfilt)
            s += "p="+row["type(r)"]+"&";
        if(ofilt)
            s += "o="+row.m.Name+"&";
        if(pmidfilt)
            s += "pmid="+row.s.PMID+"&";
        if(stypefilts.reduce((prev,curr)=>(prev||curr),false))
            s += "stypes="+row["labels(n)"].reduce((prev,curr,i)=>(stypefilts[i]?[...prev,curr]:prev),[])+"&";
        if(otypefilts.reduce((prev,curr)=>(prev||curr),false))
            s += "otypes="+row["labels(m)"].reduce((prev,curr,i)=>(otypefilts[i]?[...prev,curr]:prev),[]);
        return s;
    }
    async function expandrow()
    {
        await fetch(pyserver+"triples?"+filterstr()).then(res=>res.json()).then(data=>setnewrow(data["triples"])).catch(error=>{console.log(error);});
    }
    useEffect(()=>{if(open)expandrow();},[sfilt,pfilt,ofilt,pmidfilt,stypefilts,otypefilts]);
    return (
        <React.Fragment>
            <StyledTableRow>
                <UnpaddedTableCell>
                    <IconButton aria-label="expand row" size="small" onClick={()=>{setexpand(!open,false); expandrow();}}>
                        Explore {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </UnpaddedTableCell>
                <EntityFilters labels={row["labels(n)"]} setfilts={setstypefilts} filts={stypefilts} />
                <TripleElement filtset={setsfilt} filtval={sfilt} entname={row.n.Name} fullstring={row.s.FullString} />
                <TripleElement filtset={setpfilt} filtval={pfilt} entname={row["type(r)"]} fullstring={row["r.FullString"]} pad={true} />
                <TripleElement filtset={setofilt} filtval={ofilt} entname={row.m.Name} fullstring={row.o.FullString} pad={true} />
                <EntityFilters labels={row["labels(m)"]} setfilts={setotypefilts} filts={otypefilts} />
                <PaperFilter set={setpmidfilt} val={pmidfilt} pmid={row["s.PMID"]} title={row["title"]} />
                <CitationsFilter num={row["citedby"]} setexp={setexpand} exp={paperopen}/>
            </StyledTableRow>
            <TableRow>
                <UnpaddedTableCell>
                    <Collapse in={open||paperopen} timeout="auto" unmountOnExit>
                        <SubdirectoryArrowRightIcon />
                    </Collapse>
                </UnpaddedTableCell>
                <UnpaddedTableCell colSpan={7}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Table>
                            <TableBody>
                                {newrow.map((nrow,i)=>(<Row key={""+i} row={nrow}/>))}
                            </TableBody>
                        </Table>
                    </Collapse>
                    <Collapse in={paperopen} timeout="auto" unmountOnExit>
                        <Table>
                            <TableBody>
                                <PaperRow pmid={row["s.PMID"]} />    
                            </TableBody>
                        </Table>
                    </Collapse>
                </UnpaddedTableCell>
            </TableRow>
        </React.Fragment>
        );
}

function PaperRow(props)
{
    const {pmid,...other} = props;
    const [loaded,setloaded] = React.useState(false);
    const [cites,setcites] = React.useState({"present":[],"absent":[]});
    const [loadstr,setloadstr] = React.useState("Loading...");
    const [progress,setprogress] = React.useState(0.0);
    const [trips,settrips] = React.useState([]);
    function filterstr()
    {
        let s = "pmid=";
        for(let i = 0; i < cites["present"].length; ++i)
            s += cites["present"][i] + ",";
        for(let i = 0; i < cites["absent"].length; ++i)
            s += cites["absent"][i] + ",";
        return s;
    }
    async function getcitedby()
    {
        await fetch(pyserver+"citedbypmids?pmid="+pmid).then(res=>res.json()).then(data=>{setcites({"present":data["present"],"absent":data["absent"]})}).catch(err=>{console.log(err);});
    }
    async function gettrips()
    {
        await fetch(pyserver+"triples?"+filterstr()).then(res=>res.json()).then(data=>{settrips(data["triples"]);}).catch(error=>{console.log(error);});
    }
    async function addabstracts()
    {
        if(cites["present"].length || cites["absent"].length)
        {
            await absadd();
            setprogress(100);
            setloaded(true);
        }
    }
    async function absadd()
    {
        for(let i = 0; i < cites["absent"].length; ++i)
        {
            setloadstr(cites["absent"].length.toString()+" cited papers not currently present. Adding paper "+(i+1).toString()+"/"+cites["absent"].length.toString()+"...");
            await fetch(pyserver+"addabstract?pmid="+cites["absent"][i]);
            setprogress((i+1)*100.0/cites["absent"].length);
        }
        const newcites = {"present":[],"absent":[]};
        for(let i = 0; i < cites["present"].length; ++i)
            newcites["present"].push(cites["present"][i]);
        for(let i = 0; i < cites["absent"].length; ++i)
            newcites["present"].push(cites["absent"][i]);
        setcites(newcites);
    }
    useEffect(()=>{getcitedby();},[]);
    useEffect(()=>{if(loaded)gettrips();},[loaded]);
    useEffect(()=>{addabstracts();},[cites]);
    useEffect(()=>{console.log(cites);},[cites]);
    return (
        <React.Fragment>
            <TableRow>
                {!loaded ? (<Text><b>{loadstr}</b></Text>) : ""}
                {!loaded ?
                (<LinearProgress variant="determinate" value={progress} style={{"width":"50%"}} />)
                    : ""}
            </TableRow>
            <TableRow>
                <UnpaddedTableCell colSpan={7}>
                    <Collapse in={loaded} timeout="auto" unmountOnExit>
                        <Table>
                            <TableBody>
                                {trips.map((nrow,i)=>(<Row key={""+i} row={nrow}/>))}
                            </TableBody>
                        </Table>
                    </Collapse>
                </UnpaddedTableCell>
            </TableRow>
        </React.Fragment>
        );
}

function TabPanel(props)
{
    const {children,value,index,...other} = props;
    return (
        <div hidden={value!=index} id={index} {...other}>
            {value === index && (<Box sx={{p:3}}>{children}</Box>)}
        </div>
        );
}

function App()
{
    const [tval,settval] = React.useState(0);
    return (
        <Box sx={{width:"100%"}}>
            <Box>
                <Tabs value={tval} onChange={(event,i)=>{settval(i);}}>
                    <Tab label="Search" id={0} />
                    <Tab label="CNV" id={1} />
                    <Tab label="Cell Lines" id={2} />
                </Tabs>
            </Box>
            <TabPanel value={tval} index={0}>
                <SearchView />
            </TabPanel>
            <TabPanel value={tval} index={1}>
                <CNVView />
            </TabPanel>
            <TabPanel value={tval} index={2}>
                <CellLineView />
            </TabPanel>
        </Box>
            );
}

function SearchBox(props)
{
    const {params,paramkey,setvals,label,...other} = props;
    return (<Autocomplete
             multiple
             filterSelectedOptions
             options={(params[paramkey]||[]).map(param=>({"label":param}))}
             sx={{width:300}}
             renderInput={(args)=><TextField {...args} label={label}/>}
             onChange={(event,vals)=>{setvals(vals.map(v=>v["label"]));}}
             isOptionEqualToValue={(o,v)=>o.label===v.label} />);
}

function SearchView()
{
    const [stypefilts,setstypefilts] = useState([]);
    const [rfilts,setrfilts] = useState([]);
    const [otypefilts,setotypefilts] = useState([]);
    const [snamefilts,setsnamefilts] = useState([]);
    const [onamefilts,setonamefilts] = useState([]);
    const [params,setparams] = useState({"stypes":[],"otypes":[],"rtypes":[],"snames":[],"onames":[]});
    const [lim,setlim] = useState(10);
    const [trips,settrips] = useState([]);
    const [init,setinit] = useState(true);
    function filterstr()
    {
        let s = "";
        if(stypefilts.length)
            s += "stypes="+stypefilts.join(",")+"&";
        if(rfilts.length)
            s += "p="+rfilts.join(",")+"&";
        if(otypefilts.length)
            s += "otypes="+otypefilts.join(",")+"&";
        if(snamefilts.length)
            s += "s="+snamefilts.join(",")+"&";
        if(onamefilts.length)
            s += "o="+onamefilts.join(",");
        return s;
    }
    async function getparams(leaveout)
    {
        let nparams = {};
        await fetch(pyserver+"params?"+filterstr(leaveout)).then(res=>res.json()).then(data=>{nparams = data;}).catch(error=>{console.log(error);});
        if(leaveout !== "")
            nparams[leaveout] = params[leaveout];
        setparams(nparams);
    }
    async function gettrips(leaveout)
    {
        await fetch(pyserver+"triples?"+filterstr(leaveout)).then(res=>res.json()).then(data=>{settrips(data["triples"]);}).catch(error=>{console.log(error);});
    }
    useEffect(()=>{getparams("").then(()=>{setinit(false);});},[]);
    useEffect(()=>{if(!init)getparams("rtypes");},[rfilts]);
    useEffect(()=>{if(!init)getparams("otypes");},[otypefilts]);
    useEffect(()=>{if(!init)getparams("stypes");},[stypefilts]);
    useEffect(()=>{if(!init)getparams("snames");},[snamefilts]);
    useEffect(()=>{if(!init)getparams("onames");},[onamefilts]);
    useEffect(()=>{gettrips();},[stypefilts,otypefilts,rfilts,snamefilts,onamefilts,lim]);
    return (
        <TableContainer>
            <Table>
                <TableBody>
                    <TableRow>
                        <TableCell>
                            <Table><TableBody>
                                <TableRow><TableCell style={{borderBottom:"none"}}>
                                    <SearchBox params={params} paramkey={"stypes"} setvals={setstypefilts} label={"Entity Type"} />
                                </TableCell></TableRow>
                                <TableRow><TableCell style={{borderBottom:"none"}}>
                                    <SearchBox params={params} paramkey={"snames"} setvals={setsnamefilts} label={"Entity Name"} />
                                </TableCell></TableRow>
                            </TableBody></Table>
                        </TableCell>
                        <TableCell>
                            <SearchBox params={params} paramkey={"rtypes"} setvals={setrfilts} label={"Relationship"} />
                        </TableCell>
                        <TableCell>
                            <Table><TableBody>
                                <TableRow><TableCell style={{borderBottom:"none"}}>
                                    <SearchBox params={params} paramkey={"otypes"} setvals={setotypefilts} label={"Entity Type"} />
                                </TableCell></TableRow>
                                <TableRow><TableCell style={{borderBottom:"none"}}>
                                    <SearchBox params={params} paramkey={"onames"} setvals={setonamefilts} label={"Entity Name"} />
                                </TableCell></TableRow>
                            </TableBody></Table>
                        </TableCell>
                        <TableCell>
                            <TextField label="Results" defaultValue={10} type="number" InputLabelProps={{shrink:true}} style={{width:100}} onChange={(ev)=>{setlim(ev.target.value);}}/>
                        </TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell colSpan={4}>
                            <Table><TableBody>
                                {trips.map((row,i)=>(<Row key={""+i} row={row} />))}
                            </TableBody></Table>
                        </TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        </TableContainer>
        );
}

function CancerSelector(props)
{
    const {ctypes,setcfilts,getplot,...other} = props;
    return (<Autocomplete
             multiple
             filterSelectedOptions
             options={(ctypes||[]).map(ctype=>({"label":ctype,"ncit":ctype.split("(").at(-1).split(")")[0]}))}
             isOptionEqualToValue={(o,v)=>o.label==v.label}
             renderInput={(params)=><TextField {...params} label="Cancer Type"/>}
             onChange={(event,val)=>{setcfilts(val.map(v=>v["label"].split(" (")[0]));getplot(val.map(v=>v["label"].split(" (").at(-1).split(")")[0]));}} />);
}

function CNVPlot(props)
{
    const {plot,selpts,setselection,setselpts,...other} = props;
    if(!plot.losses.length)
        return ("");
    function selectpoints(prm)
    {
        if("xaxis.range[0]" in prm)
        {
            const pts = [];
            const idxs = [];
            let i = 0;
            for(; i < plot["xaxis"].length; ++i)
                if(plot["xaxis"][i] >= prm["xaxis.range[0]"])
                    break;
            for(; i < plot["xaxis"].length;++i)
                if(plot["xaxis"][i] >= prm["xaxis.range[1]"])
                    break;
                else
                {
                    idxs.push(i);
                    pts.push(plot["bands"][i]);
                }
            setselection([...new Set(pts)]);
            setselpts(idxs);
        }
        else
            setselection([]);
    }
    return (<Plot
             data={[{type:"bar",
                     y:plot["losses"],
                     x:plot["xaxis"],
                     marker:{color:"red"},
                     showlegend:false,
                     hoverinfo:"none",
                     customdata:plot["bands"],
                     selectedpoints:selpts},
                    {type:"bar",
                     y:plot["gains"],
                     x:plot["xaxis"],
                     marker:{color:"limegreen"},
                     showlegend:false,
                     hoverinfo:"none",
                     customdata:plot["bands"],
                     selectedpoints:selpts}]}
             layout={{scrollzoom:false,
                      barmode:"overlay",
                      selectdirection:"h",
                      dragmode:"zoom",
                      clickmode:"none",
                      xaxis:{showticklabels:false},
                      yaxis:{fixedrange:true}}}
             style={{width:"100%"}}
             config={{displayModeBar:false}}
             onRelayout={(prm)=>{selectpoints(prm);}} />);
}

function CNVTripleElement(props)
{
    const {entname,fullstring,pad,...other} = props;
    return (<TableCell style={{borderBottom:"none",padding:(pad ? 5 : 0)}}>
                <Table>
                    <TableBody>
                        <TableRow>
                            <TableCell style={{padding:"0px"}}>
                                <Text>
                                    <center><b>{entname}</b></center>
                                </Text>
                            </TableCell>
                        </TableRow>
                        <TableRow>
                            <TableCell style={{borderBottom:"none",padding:5}}><Text><center>{fullstring}</center></Text></TableCell>
                        </TableRow>
                    </TableBody>
                </Table>
            </TableCell>);
}

function CNVPaperFilter(props)
{
    const {pmid,title,...other} = props;
    return (<UnpaddedTableCell>
                <a href={"https://pubmed.ncbi.nlm.nih.gov/"+pmid} target="_blank">
                    <Text>{[...title].reduce((prev,curr,i)=>(i>50?prev:(prev+curr)),"")+"..."}</Text>
                </a>
            </UnpaddedTableCell>);
}

function GeneResult(props)
{
    const {gname,bandtrip,cancertrip,...other} = props;
    return (<StyledTableRow>
                <TableCell>
                    <Text><center><b>{gname}</b></center></Text>
                </TableCell>
                <TableCell>
                    <Table>
                        <TableBody>
                            <TableRow>
                                <TableCell><Text><center>{bandtrip["s"]}</center></Text></TableCell>
                                <TableCell><Text><center>{bandtrip["p"]}</center></Text></TableCell>
                                <TableCell><Text><center>{bandtrip["o"]}</center></Text></TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell><Text><center>{cancertrip["s"]}</center></Text></TableCell>
                                <TableCell><Text><center>{cancertrip["p"]}</center></Text></TableCell>
                                <TableCell><Text><center>{cancertrip["o"]}</center></Text></TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </TableCell>
            </StyledTableRow>);
}

function CNVRow(props)
{
    const {row,...other} = props;
    const [open,setOpen] = React.useState(false);
    const [paperopen,setpaperopen] = React.useState(false);
    const [generes,setgeneres] = React.useState([]);
    useEffect(()=>{if(open)getgeneres();},[open]);
    useEffect(()=>{console.log(generes);},[generes]);
    function setexpand(exp,papers)
    {
        setOpen(exp);
        setpaperopen(papers);
    }
    async function getgeneres()
    {
        await fetch(pyserver+"genes?"+(row["labels(n)"].includes("CytogenicBand")?("band="+row.n.Name+"&cancer="+row.m.Name):("band="+row.m.Name+"&cancer="+row.n.Name))).then(res=>res.json()).then(data=>{setgeneres(data["genes"]);}).catch(err=>{console.log(err);});
    }
    return (
        <React.Fragment>
            <StyledTableRow>
                <UnpaddedTableCell>
                    <IconButton aria-label="expand row" size="small" onClick={()=>{setOpen(!open);}}>
                        Genes {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </UnpaddedTableCell>
                <CNVTripleElement entname={row.n.Name} fullstring={row.s.FullString} />
                <CNVTripleElement entname={row["type(r)"]} fullstring={row["r.FullString"]} pad={true} />
                <CNVTripleElement entname={row.m.Name} fullstring={row.o.FullString} pad={true} />
                <CNVPaperFilter pmid={row["s.PMID"]} title={row["title"]} />
                <CitationsFilter num={row["citedby"]} setexp={setexpand} exp={paperopen} />
            </StyledTableRow>
            <TableRow>
                <UnpaddedTableCell>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <SubdirectoryArrowRightIcon />
                    </Collapse>
                </UnpaddedTableCell>
                <UnpaddedTableCell colSpan={4}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Table>
                            <TableBody>
                                {generes.map((res,i)=>(<GeneResult key={""+i} gname={res["name"]} bandtrip={res["bandtriple"]} cancertrip={res["cancertriple"]} />))}
                            </TableBody>
                        </Table>
                    </Collapse>
                </UnpaddedTableCell>
            </TableRow>
        </React.Fragment>
        );
}

function CNVView()
{
    const [cnvmatches,setcnvmatches] = useState([]);
    const [ctypes,setctypes] = useState([]);
    const [cfilts,setcfilts] = useState([]);
    const [bandfilts,setbandfilts] = useState([]);
    const [plot,setplot] = useState({"losses":[],"gains":[],"xaxis":[],"widths":[],"bands":[]});
    const [selection,setselection] = useState([]);
    const [selpts,setselpts] = useState([]);
    function filterstr()
    {
        let s = "";
        if(cfilts.length)
            s += "ctypes=" + cfilts.join(",") + "&"
        if(bandfilts.length)
            s += "bands=" + bandfilts.join(",")
        return s;
    }
    async function getplot(ncis)
    {
        await fetch(pyserver+"cnvplot"+(ctypes.length?("?nci="+ncis.join(",")):"")).then(res=>res.json()).then(data=>{setplot(data["plot"])}).catch(error=>{console.log(error);});
    }
    async function getcnvmatches()
    {
        await fetch(pyserver+"cnvmatches?"+filterstr()).then(res=>res.json()).then(data=>setcnvmatches(data["triples"])).catch(error=>{console.log(error);});
    }
    async function getcancertypes()
    {
        await fetch(pyserver+"cancertypes").then(res=>res.json()).then(data=>{setctypes(data["cancertypes"].map(o=>(o["name"]+" ("+o["id"]+")")))}).catch(error=>{console.log(error);});
    }
    useEffect(()=>{getcancertypes();},[]);
    useEffect(()=>{setselpts(plot["xaxis"].map((pt,i)=>(i)));setbandfilts([]);},[plot]);
    useEffect(()=>{setbandfilts(selection);},[selection]);
    useEffect(()=>{getcnvmatches();},[bandfilts,cfilts]);
    return (
            <TableContainer>
                <Table>
                    <TableBody>
                        <TableRow>
                            <TableCell colSpan={7}>
                                <CancerSelector ctypes={ctypes} setcfilts={setcfilts} getplot={getplot} />
                            </TableCell>
                        </TableRow>
                        <TableRow>
                            <TableCell colSpan={7}>
                                <CNVPlot plot={plot} selpts={selpts} setselection={setselection} setselpts={setselpts} />
                            </TableCell>
                        </TableRow>
                        {cnvmatches.map((row,i) => (<CNVRow key={""+i} row={row} />))}
                    </TableBody>
                </Table>
            </TableContainer>
            );
}

function CellLineSelector(props)
{
    const {clines,setcline,closes,...other} = props;
    return (<Autocomplete
             filterSelectedOptions
             options={(clines||[]).map(cline=>({"label":cline["name"],"info":cline}))}
             isOptionEqualToValue={(o,v)=>o.label==v.label}
             renderInput={(params)=><TextField {...params} label="Cell Line"/>}
             onChange={(event,val)=>{setcline(val ? val["info"] : val); closes.forEach(c=>{c(false);});}} />);
}

function CellLineView()
{
    const [clines,setclines] = React.useState([]);
    const [currcline,setcurrcline] = React.useState(null);
    const [nameexp,setnameexp] = React.useState(false);
    const [cancerexp,setcancerexp] = React.useState(false);
    const [organexp,setorganexp] = React.useState(false);
    const [pmidexp,setpmidexp] = React.useState(false);
    const [nametrips,setnametrips] = React.useState([]);
    const [cancertrips,setcancertrips] = React.useState([]);
    const [organtrips,setorgantrips] = React.useState([]);
    const [organmatches,setorganmatches] = React.useState([]);
    const [pmidtrips,setpmidtrips] = React.useState([]);
    async function getclines()
    {
        await fetch(pyserver+"celllines").then(res=>res.json()).then(data=>{setclines(data["celllines"]);}).catch(err=>{console.log(err);});
    }
    function filterstr(filt)
    {
        if(!currcline)
            return "";
        let s = "id=" + currcline["id"] + "&";
        if(filt === "cancer")
            s += "nci=" + currcline["ncit"];
        else if(filt === "organ")
            s += "organ=" + currcline["organ"];
        else if(filt === "pmid")
            s += "pmids=" + currcline["pmids"].join(",");
        return s;
    }
    async function getrow(filt)
    {
        await fetch(pyserver+"celllinematches?"+filterstr(filt)).then(res=>res.json()).then(data=>{if(filt==="name")setnametrips(data["triples"]);else if(filt==="cancer")setcancertrips(data["triples"]);else if(filt==="organ"){setorgantrips(data["triples"]);setorganmatches(data["matches"]);}else if(filt==="pmid")setpmidtrips(data["triples"]);}).catch(err=>{console.log(err);});
    }
    useEffect(()=>{getclines();},[]);
    useEffect(()=>{if(nameexp)getrow("name")},[nameexp]);
    useEffect(()=>{if(cancerexp)getrow("cancer")},[cancerexp]);
    useEffect(()=>{if(organexp)getrow("organ")},[organexp]);
    useEffect(()=>{if(pmidexp)getrow("pmid")},[pmidexp]);
    return (<TableContainer>
                <Table>
                    <TableBody>
                        <TableRow>
                            <TableCell>
                                <CellLineSelector clines={clines} setcline={setcurrcline} closes={[setnameexp,setcancerexp,setorganexp,setpmidexp]} />
                            </TableCell>
                        </TableRow>
                        {(currcline ?
                        <TableRow>
                            <TableContainer>
                                <Table style={{width:"100%"}}>
                                    <StyledTableRow>
                                        <TableCell>
                                            <center><Text><b>Name</b></Text></center>
                                        </TableCell>
                                        <TableCell>
                                            <center><Text>{currcline["name"]}</Text></center>
                                        </TableCell>
                                        <TableCell>
                                            <IconButton aria-label="expand row" size="small" onClick={()=>{setnameexp(!nameexp);}}>
                                                {nameexp ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />} Explore
                                            </IconButton>
                                        </TableCell>
                                    </StyledTableRow>
                                    <StyledTableRow>
                                        <UnpaddedTableCell colSpan={3}>
                                            <Collapse in={nameexp} timeout="auto" unmountOnExit>
                                                <Table>
                                                    <TableBody>
                                                        {nametrips.map((nrow,i)=>(<Row key={""+i} row={nrow}/>))}
                                                    </TableBody>
                                                </Table>
                                            </Collapse>
                                        </UnpaddedTableCell>
                                    </StyledTableRow>
                                    <StyledTableRow>
                                        <TableCell>
                                            <center><Text><b>Cancer Type</b></Text></center>
                                        </TableCell>
                                        <TableCell>
                                            <center><Text>{currcline["cancer"]}</Text></center>
                                        </TableCell>
                                        <TableCell>
                                            <IconButton aria-label="expand row" size="small" onClick={()=>{setcancerexp(!cancerexp);}}>
                                                {cancerexp ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />} Explore
                                            </IconButton>
                                        </TableCell>
                                    </StyledTableRow>
                                    <StyledTableRow>
                                            <UnpaddedTableCell colSpan={3}>
                                                <Collapse in={cancerexp} timeout="auto" unmountOnExit>
                                                    <Table>
                                                        <TableBody>
                                                            {cancertrips.map((nrow,i)=>(<Row key={""+i} row={nrow}/>))}
                                                        </TableBody>
                                                    </Table>
                                            </Collapse>
                                        </UnpaddedTableCell>
                                    </StyledTableRow>
                                    <StyledTableRow>
                                        <TableCell>
                                            <center><Text><b>Organ Location</b></Text></center>
                                        </TableCell>
                                        <TableCell>
                                            <center><Text>{currcline["organ"]}</Text></center>
                                        </TableCell>
                                        <TableCell>
                                            <IconButton aria-label="expand row" size="small" onClick={()=>{setorganexp(!organexp);}}>
                                                {organexp ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />} Explore
                                            </IconButton>
                                        </TableCell>
                                    </StyledTableRow>
                                    <StyledTableRow>
                                        <UnpaddedTableCell colSpan={3}>
                                            <Collapse in={organexp} timeout="auto" unmountOnExit>
                                                <Table>
                                                    <TableBody>
                                                    <StyledTableRow>
                                                        {(organmatches.length ?
                                                        <TableCell colSpan={7}>
                                                            <Text><b><center><h3>Exact Matches</h3></center></b></Text>
                                                        </TableCell> : "")}
                                                    </StyledTableRow>
                                                        {organmatches.map((nrow,i)=>(<Row key={""+i} row={nrow}/>))}
                                                    <StyledTableRow>
                                                        {(organmatches.length && organmatches.length != organtrips.length ?
                                                        <TableCell colSpan={7}>
                                                            <Text><b><center><h3>Additional Matches</h3></center></b></Text>
                                                        </TableCell> : "")}
                                                    </StyledTableRow>
                                                        {organmatches.length != organtrips.length ? (organtrips.map((nrow,i)=>(<Row key={""+i} row={nrow}/>))) : ""}
                                                    </TableBody>
                                                </Table>
                                            </Collapse>
                                        </UnpaddedTableCell>
                                    </StyledTableRow>
                                {(currcline && currcline["pmids"].length ?
                                    <StyledTableRow>
                                        <TableCell>
                                            <center><Text><b>References</b></Text></center>
                                        </TableCell>
                                        <TableCell>
                                            <center>{currcline["pmids"].map(pmid=>(<a href={"https://pubmed.ncbi.nlm.nih.gov/"+pmid} target="_blank"><Text>{pmid}</Text></a>))}</center>
                                        </TableCell>
                                        <TableCell>
                                            <IconButton aria-label="expand row" size="small" onClick={()=>{setpmidexp(!pmidexp);}}>
                                                {pmidexp ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />} Explore
                                            </IconButton>
                                        </TableCell>
                                    </StyledTableRow>
                                    : "")}
                                    <StyledTableRow>
                                            <UnpaddedTableCell colSpan={3}>
                                                <Collapse in={pmidexp} timeout="auto" unmountOnExit>
                                                    <Table>
                                                        <TableBody>
                                                            {pmidtrips.map((nrow,i)=>(<Row key={""+i} row={nrow}/>))}
                                                        </TableBody>
                                                    </Table>
                                            </Collapse>
                                        </UnpaddedTableCell>
                                    </StyledTableRow>
                                </Table>
                            </TableContainer>
                        </TableRow>
                        : "")}
                    </TableBody>
                </Table>
            </TableContainer>);
}

export default App;
