import React from 'react';
import { StaticRouter } from "react-router-dom/server";

function Router({children,url}){
    return (
    <StaticRouter location={url}>
        {children}
    </StaticRouter>
    )
}

export default Router