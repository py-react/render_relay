import React from 'react'
import { Outlet } from 'react-router-dom'
import { Layout } from '../components/BlogUI';


function AppLayout() {

    return (
        <Layout>
            <Outlet />
        </Layout>
    )
}

export default AppLayout