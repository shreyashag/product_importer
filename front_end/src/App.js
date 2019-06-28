import ReactTable from "react-table";
import "react-table/react-table.css";

import React from "react";

import axios from "axios";
import NewRecordComponent from "./NewRecordComponent";
import WebHookList from "./WebHookList";
import NewWebhookComponent from "./NewWebhookComponent";

const HEAD_URL = "http://139.59.60.234:5000/";

//function to sort the results
function filterCaseInsensitive(filter, row) {
  const id = filter.pivotId || filter.id;
  return row[id] !== undefined
    ? String(row[id].toLowerCase()).startsWith(filter.value.toLowerCase())
    : true;
}

export default class ProductList extends React.Component {
  state = {
    products: [],
    selectedFile: null,
    total: 0,
    completed: 0
  };

  constructor(props) {
    super(props);
    this.eventSource = new EventSource(HEAD_URL + "events");
    this.renderEditable = this.renderEditable.bind(this);
  }

  FileUploadProgress = () => {
    if (this.state.completed === 0 && this.state.total === 0) {
      return <h1>No Upload in progress</h1>;
    } else {
      return (
        <h1>
          Completed: {this.state.completed} Total {this.state.total}
        </h1>
      );
    }
  };

  Greeting = () => {
    const total = this.state.total;
    const completed = this.state.completed;
    return <this.FileUploadProgress total={total} completed={completed} />;
  };

  update_product_list() {
    axios.get(HEAD_URL + "product/").then(res => {
      const products = res.data;
      this.setState({ products });
    });
  }

  update_product_event_message(e) {
    let obj = JSON.parse(e.data);
    if (obj.total !== 0 && this.state.total === 0) {
      this.setState({
        total: obj.total
      });
    }
    if (Number.isInteger(obj.completed / 100) === true) {
      this.setState({
        completed: obj.completed
      });
    }

    if (obj.total > 0 && obj.completed > 0 && obj.completed === obj.total) {
      this.update_product_list();
      this.setState({
        total: 0,
        completed: 0
      });
    }
  }

  componentDidMount() {
    this.setState({
      products: [],
      selectedFile: null,
      total: 0,
      completed: 0
    });
    this.update_product_list();
    this.eventSource.onmessage = e => this.update_product_event_message(e);
  }

  onChangeHandler = event => {
    this.setState({
      selectedFile: event.target.files[0],
      loaded: 0
    });
  };

  onUpdateListHandler = event => {
    this.update_product_list();
  };

  onUploadClickHandler = () => {
    const data = new FormData();
    this.setState({});
    data.append("file", this.state.selectedFile);
    axios.post(HEAD_URL + "product/", data, {}).then(res => {
      this.setState({});
      this.update_product_list();
    });
  };

  onDeleteClickHandler = () => {
    axios.delete(HEAD_URL + "product/", {}).then(res => {
      this.update_product_list();
    });
  };

  renderEditable(cellInfo) {
    return (
      <div
        style={{ backgroundColor: "#fafafa" }}
        contentEditable
        suppressContentEditableWarning
        onBlur={e => {
          const products = [...this.state.products];
          products[cellInfo.index][cellInfo.column.id] = e.target.innerHTML;
          this.setState({ products });
        }}
        dangerouslySetInnerHTML={{
          __html: this.state.products[cellInfo.index][cellInfo.column.id]
        }}
      />
    );
  }

  handleUpdate(row) {
    var jsonPostBody = { name: row.name, description: row.description };
    axios.post(HEAD_URL + "product/" + row.sku, jsonPostBody, {}).then(res => {
      // then print response status
      if (res.status === 200) {
        this.update_product_list();
        alert("Product Updated in the database");
      }

      // this.update_product_list();
    });
  }
  handleDelete(row) {
    axios.delete(HEAD_URL + "product/" + row.sku, {}).then(res => {
      // then print response status
      if (res.status === 200) {
        this.update_product_list();
        alert("Product Deleted from Database");
      }

      // this.update_product_list();
    });
  }

  render() {
    const columns = [
      {
        Header: "SKU",
        accessor: "sku"
      },
      {
        Header: "Name",
        accessor: "name",
        Cell: this.renderEditable
      },
      {
        Header: "Description",
        accessor: "description",
        Cell: this.renderEditable
      },
      {
        Header: "",
        Cell: row => (
          <div>
            <button onClick={() => this.handleUpdate(row.original)}>
              Update
            </button>
            <button onClick={() => this.handleDelete(row.original)}>
              Delete
            </button>
          </div>
        )
      }
    ];
    return (
      <div>
        <NewWebhookComponent />
        <WebHookList />
        <NewRecordComponent />
        <div>
          <br />
          <br />
          <br />
          {/* <Products/> */}
          <h1>Product List</h1>
          <ReactTable
            filterable
            defaultFilterMethod={(filter, row) =>
              filterCaseInsensitive(filter, row)
            }
            data={this.state.products}
            columns={columns}
            defaultPageSize={10}
            pageSizeOptions={[10, 25, 50, 100, 200]}
          />
        </div>
        <div>
          <input type="file" name="file" onChange={this.onChangeHandler} />
          <button
            type="button"
            className="btn btn-success btn-block"
            onClick={this.onUploadClickHandler}
          >
            Upload
          </button>
          <button
            type="button"
            className="btn btn-error btn-block"
            onClick={this.onDeleteClickHandler}
          >
            Delete All
          </button>
          <button
            type="button"
            className="btn btn-error btn-block"
            onClick={this.onUpdateListHandler}
          >
            Update List
          </button>
          <div>
            <this.Greeting
              total={this.state.total}
              completed={this.state.completed}
            />
          </div>
        </div>
      </div>
    );
  }
}
