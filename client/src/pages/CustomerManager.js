import React, { useState } from 'react';

function CustomerManager() {
  const [customers, setCustomers] = useState([]);
  const [newCustomer, setNewCustomer] = useState({
    name: '',
    email: '',
    emailTime: '09:00'
  });

  const handleAddCustomer = (e) => {
    e.preventDefault();
    setCustomers([...customers, newCustomer]);
    setNewCustomer({ name: '', email: '', emailTime: '09:00' });
  };

  return (
    <div className="customer-manager">
      <h2>Manage Customers</h2>
      
      <form onSubmit={handleAddCustomer}>
        <input
          type="text"
          placeholder="Customer Name"
          value={newCustomer.name}
          onChange={(e) => setNewCustomer({...newCustomer, name: e.target.value})}
        />
        <input
          type="email"
          placeholder="Customer Email"
          value={newCustomer.email}
          onChange={(e) => setNewCustomer({...newCustomer, email: e.target.value})}
        />
        <input
          type="time"
          value={newCustomer.emailTime}
          onChange={(e) => setNewCustomer({...newCustomer, emailTime: e.target.value})}
        />
        <button type="submit">Add Customer</button>
      </form>

      <div className="customer-list">
        {customers.map((customer, index) => (
          <div key={index} className="customer-card">
            <h3>{customer.name}</h3>
            <p>{customer.email}</p>
            <p>Email Time: {customer.emailTime}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CustomerManager; 