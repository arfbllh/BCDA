import React from 'react'
import { Card, CardBody } from 'reactstrap'
import { Link } from 'react-router-dom'
import "./content-card.css";


const ContentCard = ({ data }) => {
    const { id, title, photo, city, price, featured, reviews } = data
    return (
        <div className='content__card'>
            <Card>
                <div className="content__img">
                    <img src={photo} alt="content-img" />
                    {featured && <span>Featured</span>}
                </div>
                <CardBody>
                    <div className="card_top d-flex align-items-center justify-content-between">
                        <span className="content__location d-flex align-items-center gap-1">
                            <i class="ri-map-pin-line"></i> {city}
                        </span>
                        <span className="content__rating d-flex align-items-center gap-1">
                            {/* <i class="ri-star-fill"></i> {avgRating ===0? null: avgRating}
                            {totalRating===0? 'Not rated': <span>({reviews.length})</span>} */}
                        </span>
                    </div>
                    <h5 className='content__title'><Link to={``}>{title}</Link></h5>
                    <div className="card__bottom d-flex align-items-center 
            justify-content-between mt-3">
                        <h5>${price} <span>/ per person</span></h5>
                        <button className="btn booking__btn">
                            <Link to={`/contents/${id}`}>Book Now</Link>
                        </button>
                    </div>
                </CardBody>
            </Card>
        </div>
    )
}

export default ContentCard