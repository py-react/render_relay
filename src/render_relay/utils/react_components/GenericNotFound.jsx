const GenericNotFound = () => {
    return (
        <div style={{
            height:"100vh",
        }} className="flex items-center justify-center bg-white dark:bg-gray-950 px-4 md:px-6">
            <div className="max-w-md text-center space-y-4">
                <h1 style={{fontSize: "8rem", lineHeight: "1", color: "rgb(17 24 39)"}} 
                    className="font-bold text-gray-900 dark:text-gray-50"
                >
                    404
                </h1>
                <p style={{fontSize: "1.125rem",color: "rgb(107 114 128)"}} className="dark:text-gray-400">
                    Oops, the page you are looking for could not be found.
                </p>
            </div>
        </div>
    )
}