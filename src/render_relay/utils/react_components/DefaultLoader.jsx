const DefaultLoader_ = ({isLoading}) => {
    const [progress, setProgress] = useState(0);
    const [loading, setLoading] = useState(isLoading);
    useEffect(() => {
        let interval;
        if (isLoading) {
            startTransition(()=>{
                setLoading(true);
                setProgress(0);
            })
            let startTime = Date.now();

            interval = setInterval(() => {
                startTransition(()=>{
                    setProgress((prev) => {
                        // Calculate elapsed time
                        const elapsedTime = Date.now() - startTime;
                        let speedFactor = 1;
    
                        // Change speed depending on how long the loader has been active
                        if (elapsedTime < 2000) {
                            // Accelerate in the first 2 seconds
                            speedFactor = 1 + Math.sin(elapsedTime / 1000) * 0.8; // Sinusoidal speed change
                        } else if (elapsedTime < 4000) {
                            // Slow down after 2 seconds
                            speedFactor = 1 - Math.sin(elapsedTime / 2000) * 0.8; // Decelerating pattern
                        }
    
                        // Prevent the progress from exceeding 100%
                        let newProgress = prev + (speedFactor * 0.8); // Adjust increment dynamically
    
                        if (newProgress >= 100) {
                            newProgress = 99; // Cap progress at 100%
                        }
                        return newProgress;
                    });
                })
            }, 50); // Interval duration can stay constant

        } else {
            // Ensure progress is completed when stopping
            startTransition(()=>{
                setProgress(99);
            })
            setTimeout(() => setLoading(false), 300); // Brief delay before setting loading to false
        }

        return () => {
            clearInterval(interval);
        };
    }, [isLoading]);

    if (!loading) return null;
    return (
        <div className="custom-backdrop">
            <div className="custom-progress-bar" style={{ width: `${{progress}}%` }}></div>
        </div>
    );
};
