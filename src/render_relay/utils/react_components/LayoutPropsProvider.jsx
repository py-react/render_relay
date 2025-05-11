
const LayoutPropsProvider = ({Element,Fallback , forUrl, ...props})=>{
    const location = useLocation();
    const [propsData,setPropsData] = useState((()=>{
        try {
            const data = JSON.parse(JSON.stringify(window.fastApi_react_app_props))
            if ("layout_props" in data){
                Object.keys(data.layout_props).map(key=>{
                    if (location.pathname.includes(key.endsWith("/") ?
                        key.substr(0,key.length-1):key) && matchPath({ path: location.pathname, exact: true },forUrl)){
                        startTransition(()=>{
                            setPropsData({...data.layout_props[key],location:props.location})
                        })
                    }
                })
            }
            return data
        }catch(err){
            if ("layout_props" in props) {
                const layouts = Object.keys(props.layout_props).filter((key) => {
                    if (location.pathname.includes(key.endsWith("/")?key.substr(0,key.length-1):key)) {
                        return { ...props.layout_props[key], location: props.location };
                    }
                });
                let currentLayoutProp = undefined
                for(let i=0;i<layouts.length;i++){
                    if(matchPath({ path: layouts[i], exact: true },forUrl)){
                        currentLayoutProp = props.layout_props[layouts[i]]
                        break
                    }
                }
                if(currentLayoutProp){
                    return currentLayoutProp
                }else{
                    return props;
                }
            } else {
                return props;
            }
        }
    })())

    useEffect(()=>{
        const data  = JSON.parse(JSON.stringify(window.fastApi_react_app_props))
        if ("layout_props" in data){
            Object.keys(data.layout_props).map(key=>{
                if (location.pathname.includes(key.endsWith("/")?key.substr(0,key.length-1):key) && matchPath({ path: location.pathname, exact: true },forUrl)){
                    startTransition(()=>{
                        setPropsData({...data.layout_props[key],location:props.location})
                    })
                }
            })
        }
    },[location])
    
    return (
        <Suspense fallback={<Fallback isLoading={true} />}>
            <Element {...propsData} />
        </Suspense>
    )
}