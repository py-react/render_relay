import React from 'react';
import { BrowserRouter } from 'react-router-dom';

function Router({children}){
    return (
    <BrowserRouter>
        {children}
    </BrowserRouter>
    )
}

export default Router