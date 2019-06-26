import React from 'react';

import axios from 'axios';

export default class ProductList extends React.Component {
  state = {
    products: []
  }

  componentDidMount() {
    axios.get(`https://jsonplaceholder.typicode.com/users`)
      .then(res => {
        const products = res.data;
        this.setState({ products });
      })
  }

  render() {
    return (
      <ul>
        { this.state.products.map(products => <li>{products.name}</li>)}
      </ul>
    )
  }
}
