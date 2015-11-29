#ifndef QIT_ITERATOR_H
#define QIT_ITERATOR_H

#include <vector>

namespace qit {

template<typename Iterator>
std::vector<typename Iterator::value_type> iterator_to_vector(const Iterator &i) {
	std::vector<typename Iterator::value_type> result;
	typename Iterator::value_type v;
	Iterator iterator(i);
	while (iterator.next(v)) {
		result.push_back(v);
	}
	return result;
}

}

#endif
