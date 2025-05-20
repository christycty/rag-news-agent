# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

# React Components
## News
| Attribute | Type    | Description                                 |
| :-------- | :------ | :------------------------------------------ |
| title     | string  | Title of the news                           |
| content   | string  | Content of the news                         |
| timestamp | number  | Timestamp when the news was posted          |
| bookmark  | boolean | Whether the user has bookmarked the article |
| link      | string  | Link to the original article                |
| site      | string  | Site of the article                         |

## Message
It contains of `text` and any number of `news` components. 
