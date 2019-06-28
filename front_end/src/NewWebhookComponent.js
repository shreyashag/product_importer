import "react-table/react-table.css";

import React from "react";

import axios from "axios";

const HEAD_URL = "http://localhost:5000/";

export default class NewWebhookComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { url: "" };
    this.handleChangeURL = this.handleChangeURL.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChangeURL(event) {
    this.setState({ url: event.target.value });
  }

  handleSubmit(event) {
    var jsonPostBody = { url: this.state.url };
    event.preventDefault();
    axios.post(HEAD_URL + "webhook/", jsonPostBody, {}).then(res => {
      // then print response status
      if (res.status === 200) {
        alert("Webhook added successfully");
        this.setState({
          url: ""
        });
      }

      // this.update_product_list();
    });
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <h1> Insert New Webhook</h1>
        <label>
          URL:
          <input
            type="text"
            value={this.state.url}
            onChange={this.handleChangeURL}
          />
        </label>
        <input type="submit" value="Submit" />
      </form>
    );
  }
}
