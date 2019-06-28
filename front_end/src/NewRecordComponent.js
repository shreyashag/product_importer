import "react-table/react-table.css";

import React from "react";

import axios from "axios";

const HEAD_URL = "http://139.59.60.234:5000/";

export default class NewRecordComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { sku: "", name: "", description: "" };

    this.handleChangeSku = this.handleChangeSku.bind(this);
    this.handleChangeName = this.handleChangeName.bind(this);
    this.handleChangeDescription = this.handleChangeDescription.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChangeSku(event) {
    this.setState({ sku: event.target.value });
  }
  handleChangeName(event) {
    this.setState({ name: event.target.value });
  }
  handleChangeDescription(event) {
    this.setState({ description: event.target.value });
  }

  handleSubmit(event) {
    var jsonPostBody = {
      sku: this.state.sku,
      name: this.state.name,
      description: this.state.description
    };
    event.preventDefault();
    axios.put(HEAD_URL + "product/", jsonPostBody, {}).then(res => {
      // then print response status
      if (res.status === 200) {
        alert("Record upserted into the database correctly");
        this.setState({
          sku: "",
          name: "",
          description: ""
        });
      }

      // this.update_product_list();
    });
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <h1> Insert New Product</h1>
        <label>
          SKU:
          <input
            type="text"
            value={this.state.sku}
            onChange={this.handleChangeSku}
          />
        </label>
        <label>
          Name:
          <input
            type="text"
            value={this.state.name}
            onChange={this.handleChangeName}
          />
        </label>
        <label>
          Description:
          <input
            type="text"
            value={this.state.description}
            onChange={this.handleChangeDescription}
          />
        </label>
        <input type="submit" value="Submit" />
      </form>
    );
  }
}
