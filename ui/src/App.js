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
import TableRow from '@mui/material/TableRow';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import SubdirectoryArrowRightIcon from '@mui/icons-material/SubdirectoryArrowRight';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import Plot from 'react-plotly.js';
import { Button } from '@mui/material';
import Paper from '@mui/material/Paper';
import TableHead from '@mui/material/TableHead';


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
    
    
    //function findCitations()
    //{
     //   return fetch(pyserver+"citedby?pmid="+pmid).then(res=>res.json()).then(data=>setcitedby(data["citedby"])).catch(error=>{console.log(error);});
    //}
    return (<UnpaddedTableCell hover onClick={()=>{set(!val);}}>
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
            </UnpaddedTableCell>);
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
    const {row} = props;
    const [open,setOpen] = React.useState(false);
    const [newrow,setnewrow] = React.useState([]);
    const [sfilt,setsfilt] = React.useState(false);
    const [pfilt,setpfilt] = React.useState(false);
    const [ofilt,setofilt] = React.useState(false);
    const [pmidfilt,setpmidfilt] = React.useState(false);
    const [stypefilts,setstypefilts] = React.useState(row["labels(n)"].map((ty)=>(false)));
    const [otypefilts,setotypefilts] = React.useState(row["labels(m)"].map((ty)=>(false)));
    const [citedBy, setCitedBy] = useState();
    const [clicked, setClicked] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [paperids, setPaperids] = useState([]);

    const togglePopup = () => {
        setIsOpen(!isOpen);
        if (isOpen) {
        }
      }

    const handleClick = (pmid) => {
        if (clicked) {
            setClicked(false);
        } else {
            setClicked(true);
            findCitations(pmid);
        }
    };

    const findCitations = async (pmid) => {
        try {
            const response = await fetch(
                pyserver+`citedby?pmid=`+pmid
            );
            
            const citations = await response.json();
            console.log('This is the fetch', citations)
            setCitedBy(citations.citedby);
            setPaperids(citations.paper_ids);
        }
        catch (error) {
            console.log('Failed to fetch citations', error);
        }
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

    const Popup = props => {
        return (
          <div className="popup-box">
            <div className="box">
                <span className="close-icon" onClick={props.handleClose}>x</span>
                <h2>Paper with id {props.pmid} is cited totally by {<p style={{color: 'red'}}>{props.citedBy} pubmed papers</p>}</h2>
                <TableContainer component={Paper}>
                    <Table sx={{ minWidth: 150 }} aria-label="simple table" rowP>
                        <TableHead className="table-header">
                            <TableRow>
                                <TableCell>PUBMED ID</TableCell>
                                <TableCell>Article link in pubmed</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                        {paperids.map((id) => (
                           <TableRow key={id} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                                <TableCell component="th" scope="row">
                                    {id}
                                </TableCell>
                                <TableCell>
                                    <a href={"https://pubmed.ncbi.nlm.nih.gov/"+id} target="_blank">
                                        https://pubmed.ncbi.nlm.nih.gov/{id}
                                    </a>
                                </TableCell>
                           </TableRow>
                        ))}
                        </TableBody>
                    </Table>
    </TableContainer>
            </div>
          </div>
        );
      };
    
    async function expandrow()
    {
        await fetch(pyserver+"triples?"+filterstr()).then(res=>res.json()).then(data=>setnewrow(data["triples"])).catch(error=>{console.log(error);});
    }
    useEffect(()=>{if(open)expandrow();},[sfilt,pfilt,ofilt,pmidfilt,stypefilts,otypefilts]);
    return (
        <React.Fragment>
            <StyledTableRow>
                <UnpaddedTableCell>
                    <IconButton aria-label="expand row" size="small" onClick={()=>{setOpen(!open); expandrow();}}>
                        Explore {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                    </IconButton>
                </UnpaddedTableCell>
                <EntityFilters labels={row["labels(n)"]} setfilts={setstypefilts} filts={stypefilts} />
                <TripleElement filtset={setsfilt} filtval={sfilt} entname={row.n.Name} fullstring={row.s.FullString} />
                <TripleElement filtset={setpfilt} filtval={pfilt} entname={row["type(r)"]} fullstring={row["r.FullString"]} pad={true} />
                <TripleElement filtset={setofilt} filtval={ofilt} entname={row.m.Name} fullstring={row.o.FullString} pad={true} />
                <EntityFilters labels={row["labels(m)"]} setfilts={setotypefilts} filts={otypefilts} />
                <PaperFilter set={setpmidfilt} val={pmidfilt} pmid={row["s.PMID"]} title={row["title"]} />
                <Button color='inherit' onClick={() => handleClick(row["s.PMID"])}>Cited by {clicked ? <h4 style={{color: 'red'}}>{citedBy} pubmed papers</h4> : <span></span>}</Button>
                {clicked && <input type="button" value="Click for more" onClick={togglePopup}/>}
                {isOpen && clicked && <Popup pmid={row["s.PMID"]} clicked ={clicked} citedBy={citedBy} handleClose={togglePopup}/>}
            </StyledTableRow>
            <TableRow>
                <UnpaddedTableCell>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <SubdirectoryArrowRightIcon />
                    </Collapse>
                </UnpaddedTableCell>
                <UnpaddedTableCell colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Table>
                            <TableBody>
                                {newrow.map((nrow,i)=>(<Row key={""+i} row={nrow}/>))}
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
                </Tabs>
            </Box>
            <TabPanel value={tval} index={0}>
                <SearchView />
            </TabPanel>
            <TabPanel value={tval} index={1}>
                <CNVView />
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
        console.log('HI', trips)
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
                        {cnvmatches.map((row,i) => (<Row key={""+i} row={row} />))}
                    </TableBody>
                </Table>
            </TableContainer>
            );
}

export default App;
