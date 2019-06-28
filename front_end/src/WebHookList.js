import React from "react";
import ReactTable from "react-table";
import "react-table/react-table.css";

import axios from "axios";
const HEAD_URL = "http://localhost:5000/";
export default class WebHookList extends React.Component {
  state = {
    products: []
  };

  updateWebhookList() {
    axios.get(HEAD_URL + "webhook/").then(res => {
      const products = res.data;
      this.setState({ products });
    });
  }

  componentDidMount() {
    this.updateWebhookList();
  }

  handleDelete(row) {
    // console.log(row);
    axios.delete(HEAD_URL + "webhook/" + row.id).then(res => {
      // const products = res.data;
      // this.setState({ products });
      this.updateWebhookList();
    });
  }

  render() {
    const columns = [
      {
        Header: "ID",
        accessor: "id"
      },
      {
        Header: "URL",
        accessor: "url"
      },
      {
        Header: "",
        Cell: row => (
          <div>
            <button onClick={() => this.handleDelete(row.original)}>
              Delete
            </button>
          </div>
        )
      }
    ];
    return (
      <div>
        <ReactTable
          // filterable
          // defaultFilterMethod={(filter, row) =>
          //   filterCaseInsensitive(filter, row)
          // }
          data={this.state.products}
          columns={columns}
          defaultPageSize={5}
          pageSizeOptions={[5, 10, 20, 100]}
        />
        <button
          type="button"
          className="btn btn-error btn-block"
          onClick={this.onUpdateListHandler}
        >
          Update List
        </button>
      </div>
    );
  }
}
