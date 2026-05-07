
const PropsProvider = ({Element,Fallback,...props})=>{
    const location = useLocation()
    const [loading,setLoading] = useState(false)

    const [propsData,setPropData] = useState(()=>(()=>{
        try {
            const data = JSON.parse(JSON.stringify(window.fastApi_react_app_props))
            return data
        }catch(err){
            return props
        }
    })())

    useEffect(()=>{
        React.startTransition(()=>{
            const data  = JSON.parse(JSON.stringify(window.fastApi_react_app_props))
            setPropData(data)
            setLoading(false)
        })
        return ()=>{
            setLoading(false)
        }
    },[location])

    useEffect(() => {
        // Define a function to update the loading state
        const handleLoadingEvent = (event) => {
            React.startTransition(()=>{
                setLoading(event.detail);  // Update state based on the event's detail
            })
        };

        // Listen for the custom event on the window object
        window.addEventListener('loadingEvent', handleLoadingEvent);

        // Clean up the event listener when the component unmounts
        return () => {
            window.removeEventListener('loadingEvent', handleLoadingEvent);
        };
    }, []);

    return (
        <Suspense fallback={<Fallback isLoading={true} />}>
            <Element {...propsData} />
            <Fallback isLoading={loading} />
        </Suspense>
    )
}