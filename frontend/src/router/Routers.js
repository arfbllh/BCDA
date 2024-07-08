import React from 'react'
import {Routes, Route, Navigate} from 'react-router-dom'
import Home from '../Pages/Home'
import About from '../Pages/about'
import Query from '../Pages/query'
import Result from '../Pages/result'
import ResultView from '../Pages/result-view'


const Routers = () => {
  return (
    <Routes>
       <Route path ='/' element={<Navigate to = '/home' />}/>
       <Route path='/home' element={<Home/>}/>
       <Route path='/about' element={<About/>}/>
       <Route path='/query' element={<Query/>}/>
       <Route path='/result' element={<Result/>}/>
       <Route path='/result-view' element={<ResultView/>}/>
    </Routes>
  )
}

export default Routers